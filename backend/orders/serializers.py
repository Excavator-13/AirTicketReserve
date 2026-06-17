import re
from decimal import Decimal

from rest_framework import serializers
from flights.models import Flight, CabinClass
from flights.serializers import AirportSerializer, CabinClassDetailSerializer
from orders.models import Order, Passenger, AddonService, Payment
from refunds.models import RefundRequest
from reschedules.models import RescheduleRequest


class PassengerWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    id_type = serializers.ChoiceField(choices=['ID_CARD', 'PASSPORT'])
    id_number = serializers.CharField(max_length=50)
    passenger_type = serializers.ChoiceField(choices=['ADULT', 'CHILD', 'INFANT'])

    def validate(self, attrs):
        id_type = attrs.get('id_type', '')
        id_number = attrs.get('id_number', '')
        if id_type == 'ID_CARD':
            if not re.match(r'^\d{17}[\dXx]$', id_number):
                raise serializers.ValidationError({'id_number': '身份证号格式不正确'})
        elif id_type == 'PASSPORT':
            if not re.match(r'^[A-Za-z0-9]{5,20}$', id_number):
                raise serializers.ValidationError({'id_number': '护照号格式不正确'})
        return attrs


class AddonServiceWriteSerializer(serializers.Serializer):
    service_name = serializers.CharField(max_length=100)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)


class CreateOrderSerializer(serializers.Serializer):
    flight_id = serializers.UUIDField()
    cabin_id = serializers.UUIDField()
    passengers = PassengerWriteSerializer(many=True)
    addon_services = AddonServiceWriteSerializer(many=True, required=False, default=[])

    def validate_flight_id(self, value):
        if not Flight.objects.filter(pk=value).exists():
            raise serializers.ValidationError('航班不存在')
        return value

    def validate_cabin_id(self, value):
        if not CabinClass.objects.filter(pk=value).exists():
            raise serializers.ValidationError('舱位不存在')
        return value

    def validate_passengers(self, value):
        if not value:
            raise serializers.ValidationError('至少需要一名乘机人')
        return value


class PassengerReadSerializer(serializers.ModelSerializer):
    flight_no = serializers.CharField(source='flight.flight_no', read_only=True, default=None)
    departure_city = serializers.SerializerMethodField()
    arrival_city = serializers.SerializerMethodField()
    departure_time = serializers.DateTimeField(source='flight.departure_time', read_only=True, default=None)
    cabin_class_type = serializers.CharField(source='cabin_class.class_type', read_only=True, default=None)

    class Meta:
        model = Passenger
        fields = (
            'id', 'name', 'id_type', 'id_number', 'passenger_type',
            'ticket_no', 'status', 'flight_no', 'departure_city',
            'arrival_city', 'departure_time', 'cabin_class_type',
        )

    def get_departure_city(self, obj):
        return obj.flight.departure_airport.city if obj.flight else None

    def get_arrival_city(self, obj):
        return obj.flight.arrival_airport.city if obj.flight else None


class AddonServiceReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddonService
        fields = ('id', 'service_name', 'price')


class OrderListSerializer(serializers.ModelSerializer):
    departure_city = serializers.SerializerMethodField()
    arrival_city = serializers.SerializerMethodField()
    departure_time = serializers.SerializerMethodField()
    flight_no = serializers.SerializerMethodField()
    remaining_seconds = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id', 'order_no', 'status', 'total_amount',
            'departure_city', 'arrival_city', 'departure_time',
            'flight_no', 'remaining_seconds', 'created_at',
        )

    def get_departure_city(self, obj):
        return obj.flight.departure_airport.city if obj.flight else ''

    def get_arrival_city(self, obj):
        return obj.flight.arrival_airport.city if obj.flight else ''

    def get_departure_time(self, obj):
        return obj.flight.departure_time.isoformat() if obj.flight else ''

    def get_flight_no(self, obj):
        return obj.flight.flight_no if obj.flight else ''

    def get_remaining_seconds(self, obj):
        if obj.status != 'PENDING':
            return None
        from django.utils import timezone
        now = timezone.now()
        if obj.pay_expire_at and obj.pay_expire_at > now:
            return int((obj.pay_expire_at - now).total_seconds())
        return 0


class OrderDetailSerializer(serializers.ModelSerializer):
    flight_no = serializers.CharField(source='flight.flight_no', read_only=True)
    airline = serializers.CharField(source='flight.airline', read_only=True)
    departure_airport = AirportSerializer(source='flight.departure_airport', read_only=True)
    arrival_airport = AirportSerializer(source='flight.arrival_airport', read_only=True)
    departure_time = serializers.DateTimeField(source='flight.departure_time', read_only=True)
    arrival_time = serializers.DateTimeField(source='flight.arrival_time', read_only=True)
    aircraft_type = serializers.CharField(source='flight.aircraft_type', read_only=True)
    is_direct = serializers.BooleanField(source='flight.is_direct', read_only=True)
    cabin_info = CabinClassDetailSerializer(source='cabin_class', read_only=True)
    passengers = PassengerReadSerializer(many=True, read_only=True)
    addon_services = AddonServiceReadSerializer(many=True, read_only=True)
    remaining_seconds = serializers.SerializerMethodField()
    can_refund = serializers.SerializerMethodField()
    can_reschedule = serializers.SerializerMethodField()
    addon_total = serializers.SerializerMethodField()
    refund_total = serializers.SerializerMethodField()
    refund_fee_total = serializers.SerializerMethodField()
    reschedule_fee_total = serializers.SerializerMethodField()
    reschedule_diff_total = serializers.SerializerMethodField()
    paid_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id', 'order_no', 'status', 'total_amount',
            'pay_expire_at', 'created_at', 'updated_at',
            'flight_no', 'airline',
            'departure_airport', 'arrival_airport',
            'departure_time', 'arrival_time', 'aircraft_type', 'is_direct',
            'cabin_info', 'passengers', 'addon_services',
            'remaining_seconds', 'can_refund', 'can_reschedule',
            'addon_total', 'refund_total', 'refund_fee_total',
            'reschedule_fee_total', 'reschedule_diff_total', 'paid_amount',
        )

    def get_remaining_seconds(self, obj):
        if obj.status != 'PENDING':
            return None
        from django.utils import timezone
        now = timezone.now()
        if obj.pay_expire_at and obj.pay_expire_at > now:
            return int((obj.pay_expire_at - now).total_seconds())
        return 0

    def get_can_refund(self, obj):
        if obj.status == 'TICKETED':
            normal_passengers = obj.passengers.filter(status='NORMAL').exists()
            return normal_passengers
        return False

    def get_can_reschedule(self, obj):
        if obj.status == 'TICKETED':
            normal_passengers = obj.passengers.filter(status='NORMAL').exists()
            return normal_passengers
        return False

    def get_addon_total(self, obj):
        pax_count = obj.passengers.count()
        total = Decimal('0.00')
        for svc in obj.addon_services.all():
            total += svc.price * pax_count
        return str(total.quantize(Decimal('0.01')))

    def get_refund_total(self, obj):
        total = Decimal('0.00')
        for req in obj.refund_requests.all():
            if req.status == 'APPROVED':
                total += req.refund_amount
        return str(total.quantize(Decimal('0.01')))

    def get_refund_fee_total(self, obj):
        total = Decimal('0.00')
        for req in obj.refund_requests.all():
            if req.status == 'APPROVED':
                total += req.fee
        return str(total.quantize(Decimal('0.01')))

    def get_reschedule_fee_total(self, obj):
        total = Decimal('0.00')
        for req in obj.reschedule_requests.all():
            if req.status == 'COMPLETED':
                total += req.fee
        return str(total.quantize(Decimal('0.01')))

    def get_reschedule_diff_total(self, obj):
        total = Decimal('0.00')
        for req in obj.reschedule_requests.all():
            if req.status == 'COMPLETED':
                total += req.price_difference
        return str(total.quantize(Decimal('0.01')))

    def get_paid_amount(self, obj):
        refund_total = Decimal(self.get_refund_total(obj))
        reschedule_diff_total = Decimal(self.get_reschedule_diff_total(obj))
        reschedule_fee_total = Decimal(self.get_reschedule_fee_total(obj))
        paid = obj.total_amount - refund_total + reschedule_diff_total + reschedule_fee_total
        return str(paid.quantize(Decimal('0.01')))


class PayOrderSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    method = serializers.CharField(max_length=30, default='MOCK_ALIPAY')


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'payment_no', 'amount', 'method', 'status', 'paid_at')


class RefundApplySerializer(serializers.Serializer):
    passenger_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )


class RescheduleApplySerializer(serializers.Serializer):
    passenger_id = serializers.UUIDField()
    new_flight_id = serializers.UUIDField()
    new_cabin_id = serializers.UUIDField()

    def validate_new_flight_id(self, value):
        if not Flight.objects.filter(pk=value).exists():
            raise serializers.ValidationError('新航班不存在')
        return value

    def validate_new_cabin_id(self, value):
        if not CabinClass.objects.filter(pk=value).exists():
            raise serializers.ValidationError('新舱位不存在')
        return value