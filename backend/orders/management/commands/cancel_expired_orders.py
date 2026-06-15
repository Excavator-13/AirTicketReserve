from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from orders.models import Order
from flights.models import CabinClass
from notifications.models import Notification


class Command(BaseCommand):
    help = '扫描并取消超时未支付的订单，释放库存'

    def handle(self, *args, **options):
        now = timezone.now()
        expired_orders = Order.objects.filter(
            status='PENDING',
            pay_expire_at__lt=now,
        )

        count = 0
        for order in expired_orders:
            with transaction.atomic():
                passenger_count = order.passengers.count()
                CabinClass.increase_available_seats(order.cabin_class_id, passenger_count)

                order.status = 'CANCELLED'
                order.save(update_fields=['status', 'updated_at'])

                Notification.objects.create(
                    user=order.user,
                    title='订单已取消',
                    content=f'您的订单 {order.order_no} 因超时未支付已自动取消。',
                    related_order=order,
                )

                count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'订单 {order.order_no} 已取消，释放 {passenger_count} 个座位'
                ))

        self.stdout.write(self.style.SUCCESS(
            f'扫描完成，共取消 {count} 个超时订单'
        ))