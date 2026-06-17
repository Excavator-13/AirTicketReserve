from datetime import timedelta
from decimal import Decimal

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from django.db import transaction
from django.utils import timezone

from common.responses import UnifiedResponse
from common.permissions import IsOwner
from common.business_exceptions import ConflictError, BusinessValidationError
from flights.models import Flight, CabinClass
from orders.models import Order, Passenger, Payment
from orders.serializers import (
    CreateOrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    PayOrderSerializer,
    RefundApplySerializer,
    RescheduleApplySerializer,
    PassengerReadSerializer,
)
from notifications.models import Notification


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    serializer_class = OrderListSerializer

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).select_related(
            'flight__departure_airport', 'flight__arrival_airport', 'cabin_class'
        ).prefetch_related(
            'addon_services',
            'refund_requests', 'reschedule_requests',
            'passengers__flight__departure_airport',
            'passengers__flight__arrival_airport',
            'passengers__cabin_class',
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateOrderSerializer
        if self.action == 'retrieve':
            return OrderDetailSerializer
        if self.action in ('pay', 'refund', 'reschedule'):
            return OrderDetailSerializer
        return OrderListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        start_date = request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)

        end_date = request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return UnifiedResponse.success(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrderDetailSerializer(instance)
        return UnifiedResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        flight_id = serializer.validated_data['flight_id']
        cabin_id = serializer.validated_data['cabin_id']
        passengers_data = serializer.validated_data['passengers']
        addon_services_data = serializer.validated_data.get('addon_services', [])

        try:
            flight = Flight.objects.get(pk=flight_id)
        except Flight.DoesNotExist:
            raise BusinessValidationError(detail='航班不存在', data=None)

        try:
            cabin_class = CabinClass.objects.get(pk=cabin_id)
        except CabinClass.DoesNotExist:
            raise BusinessValidationError(detail='舱位不存在', data=None)

        if cabin_class.flight_id != flight_id:
            raise BusinessValidationError(detail='舱位不属于所选航班', data=None)

        passenger_count = len(passengers_data)
        if cabin_class.available_seats < passenger_count:
            raise ConflictError(
                detail='库存不足',
                data={'requested': passenger_count, 'available': cabin_class.available_seats},
            )

        order = Order.create_order(
            user=request.user,
            flight=flight,
            cabin_class=cabin_class,
            passengers_data=passengers_data,
            addon_services_data=addon_services_data if addon_services_data else None,
        )

        result_serializer = OrderDetailSerializer(order)
        return UnifiedResponse.success(data=result_serializer.data, code=201)

    @action(detail=True, methods=['post'], url_path='pay')
    def pay(self, request, pk=None):
        order = self.get_object()

        if order.status != 'PENDING':
            raise ConflictError(
                detail='该订单已支付，请勿重复操作',
                data={'status': order.status},
            )

        from django.utils import timezone
        if order.pay_expire_at and order.pay_expire_at < timezone.now():
            raise ConflictError(
                detail='订单已超时，无法支付',
                data={'status': order.status},
            )

        pay_serializer = PayOrderSerializer(data=request.data)
        pay_serializer.is_valid(raise_exception=True)

        submitted_amount = pay_serializer.validated_data['amount']
        method = pay_serializer.validated_data['method']

        if submitted_amount != order.total_amount:
            raise BusinessValidationError(
                detail='支付金额校验失败',
                data={
                    'expected': str(order.total_amount),
                    'actual': str(submitted_amount),
                },
            )

        with transaction.atomic():
            payment_no = Payment.generate_payment_no()
            Payment.objects.create(
                payment_no=payment_no,
                order=order,
                amount=submitted_amount,
                method=method,
                status='SUCCESS',
                paid_at=timezone.now(),
            )

            order.status = 'PAID'
            order.save(update_fields=['status', 'updated_at'])

            base_count = Passenger.objects.count()
            for idx, passenger in enumerate(order.passengers.all()):
                ticket_no = f'TKT{timezone.now().strftime("%Y%m%d")}{base_count + idx + 1:06d}'
                passenger.ticket_no = ticket_no
                passenger.save(update_fields=['ticket_no'])

            order.status = 'TICKETED'
            order.save(update_fields=['status', 'updated_at'])

        Notification.objects.create(
            user=order.user,
            title='出票成功',
            content=f'您的订单 {order.order_no} 已出票成功，祝您旅途愉快！',
            related_order=order,
        )

        return UnifiedResponse.success(
            data={'order_no': order.order_no, 'status': order.status},
            msg='支付成功，已出票',
        )

    @action(detail=True, methods=['post'], url_path='refund')
    def refund(self, request, pk=None):
        order = self.get_object()

        if order.status != 'TICKETED':
            raise ConflictError(
                detail=f'该订单状态为 {order.status}，无法退票',
                data={'status': order.status},
            )

        refund_serializer = RefundApplySerializer(data=request.data)
        refund_serializer.is_valid(raise_exception=True)

        passenger_ids = refund_serializer.validated_data['passenger_ids']

        total_refund = Decimal('0.00')
        total_fee = Decimal('0.00')
        refunded_passengers = []

        with transaction.atomic():
            for pid in passenger_ids:
                try:
                    passenger = order.passengers.get(pk=pid)
                except Passenger.DoesNotExist:
                    raise BusinessValidationError(
                        detail='乘机人不存在或不属于该订单',
                        data=None,
                    )

                if passenger.status != 'NORMAL':
                    raise ConflictError(
                        detail=f'乘机人 {passenger.name} 状态为 {passenger.get_status_display()}，无法退票',
                        data={'passenger_status': passenger.status},
                    )

                now = timezone.now()
                passenger_flight = passenger.flight or order.flight
                passenger_cabin = passenger.cabin_class or order.cabin_class
                hours_before = (passenger_flight.departure_time - now).total_seconds() / 3600

                fee = passenger_cabin.calculate_refund_fee(hours_before)
                ticket_price = passenger_cabin.base_price + passenger_cabin.tax + passenger_cabin.fuel_surcharge
                refund_amount = ticket_price - fee

                from refunds.models import RefundRequest
                RefundRequest.objects.create(
                    order=order,
                    passenger=passenger,
                    refund_amount=refund_amount,
                    fee=fee,
                    status='APPROVED',
                )

                passenger.status = 'REFUNDED'
                passenger.save(update_fields=['status'])

                CabinClass.increase_available_seats(passenger_cabin.pk, 1)

                total_refund += refund_amount
                total_fee += fee
                refunded_passengers.append(passenger.name)

            has_active = Passenger.objects.filter(
                order=order
            ).exclude(
                status__in=['REFUNDED', 'RESCHEDULED']
            ).exists()
            if not has_active:
                order.status = 'REFUNDED'
                order.save(update_fields=['status', 'updated_at'])

        Notification.objects.create(
            user=order.user,
            title='退票成功',
            content=f'您的订单 {order.order_no} 中乘机人 {", ".join(refunded_passengers)} 已退票成功，预计退款 ¥{total_refund}。',
            related_order=order,
        )

        return UnifiedResponse.success(
            data={
                'refund_amount': str(total_refund),
                'fee': str(total_fee),
            },
            msg='退票成功',
        )

    @action(detail=True, methods=['post'], url_path='reschedule')
    def reschedule(self, request, pk=None):
        order = self.get_object()

        if order.status != 'TICKETED':
            raise ConflictError(
                detail=f'该订单状态为 {order.status}，无法改签',
                data={'status': order.status},
            )

        reschedule_serializer = RescheduleApplySerializer(data=request.data)
        reschedule_serializer.is_valid(raise_exception=True)

        passenger_id = reschedule_serializer.validated_data['passenger_id']
        new_flight_id = reschedule_serializer.validated_data['new_flight_id']
        new_cabin_id = reschedule_serializer.validated_data['new_cabin_id']

        try:
            passenger = order.passengers.get(pk=passenger_id)
        except Passenger.DoesNotExist:
            raise BusinessValidationError(
                detail='乘机人不存在或不属于该订单',
                data=None,
            )

        if passenger.status != 'NORMAL':
            raise ConflictError(
                detail=f'该乘机人状态为 {passenger.get_status_display()}，无法改签',
                data={'passenger_status': passenger.status},
            )

        try:
            new_flight = Flight.objects.get(pk=new_flight_id)
        except Flight.DoesNotExist:
            raise BusinessValidationError(detail='新航班不存在', data=None)

        try:
            new_cabin = CabinClass.objects.get(pk=new_cabin_id)
        except CabinClass.DoesNotExist:
            raise BusinessValidationError(detail='新舱位不存在', data=None)

        if new_cabin.flight_id != new_flight_id:
            raise BusinessValidationError(detail='新舱位不属于所选航班', data=None)

        if new_cabin.available_seats < 1:
            raise ConflictError(
                detail='新航班舱位库存不足',
                data={'available_seats': new_cabin.available_seats},
            )

        now = timezone.now()
        passenger_flight = passenger.flight or order.flight
        passenger_cabin = passenger.cabin_class or order.cabin_class
        hours_before = (passenger_flight.departure_time - now).total_seconds() / 3600

        reschedule_fee = passenger_cabin.calculate_reschedule_fee(hours_before)

        old_ticket_price = passenger_cabin.base_price + passenger_cabin.tax + passenger_cabin.fuel_surcharge
        new_ticket_price = new_cabin.base_price + new_cabin.tax + new_cabin.fuel_surcharge
        price_difference = new_ticket_price - old_ticket_price

        total_pay = reschedule_fee + max(price_difference, Decimal('0.00'))

        with transaction.atomic():
            CabinClass.decrease_available_seats(new_cabin_id, 1)
            CabinClass.increase_available_seats(passenger_cabin.pk, 1)

            from reschedules.models import RescheduleRequest
            RescheduleRequest.objects.create(
                order=order,
                passenger=passenger,
                new_flight=new_flight,
                new_cabin=new_cabin,
                price_difference=price_difference,
                fee=reschedule_fee,
                status='COMPLETED',
            )

            passenger.status = 'RESCHEDULED'
            if passenger.ticket_no:
                passenger.ticket_no = passenger.ticket_no + '-VOID'
            passenger.save(update_fields=['status', 'ticket_no'])

            new_ticket_no = f'TKT{timezone.now().strftime("%Y%m%d")}{Passenger.objects.count() + 1:06d}'
            new_passenger = Passenger.objects.create(
                order=order,
                name=passenger.name,
                id_type=passenger.id_type,
                id_number=passenger.id_number,
                passenger_type=passenger.passenger_type,
                ticket_no=new_ticket_no,
                status='NORMAL',
                flight=new_flight,
                cabin_class=new_cabin,
            )

        Notification.objects.create(
            user=order.user,
            title='改签成功',
            content=f'您的订单 {order.order_no} 中乘机人 {passenger.name} 已改签至 {new_flight.flight_no}，新票号 {new_passenger.ticket_no}。',
            related_order=order,
        )

        return UnifiedResponse.success(
            data={
                'price_difference': str(price_difference),
                'fee': str(reschedule_fee),
                'total_pay': str(total_pay),
            },
            msg='改签成功',
        )

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        order = self.get_object()

        if order.status != 'PENDING':
            raise ConflictError(
                detail=f'该订单状态为 {order.status}，无法取消',
                data={'status': order.status},
            )

        with transaction.atomic():
            order.status = 'CANCELLED'
            order.save(update_fields=['status', 'updated_at'])

            CabinClass.increase_available_seats(order.cabin_class_id, order.passengers.count())

        Notification.objects.create(
            user=order.user,
            title='订单已取消',
            content=f'您的订单 {order.order_no} 已取消，舱位库存已释放。',
            related_order=order,
        )

        return UnifiedResponse.success(
            data={'order_no': order.order_no, 'status': order.status},
            msg='订单已取消',
        )

    def destroy(self, request, *args, **kwargs):
        return UnifiedResponse.error(msg='不允许删除订单', code=403)

    def update(self, request, *args, **kwargs):
        return UnifiedResponse.error(msg='不允许修改订单', code=403)