import uuid
from datetime import timedelta
from decimal import Decimal

from django.db import models, transaction
from django.utils import timezone

from flights.models import CabinClass


class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', '待支付'),
        ('PAID', '已支付/出票中'),
        ('TICKETED', '已出票'),
        ('REFUNDING', '退票中'),
        ('REFUNDED', '已退票'),
        ('RESCHEDULED', '已改签'),
        ('CANCELLED', '已取消'),
    )

    VALID_TRANSITIONS = {
        'PENDING': ['PAID', 'CANCELLED'],
        'PAID': ['TICKETED'],
        'TICKETED': ['REFUNDING', 'RESCHEDULED'],
        'REFUNDING': ['REFUNDED'],
    }

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    order_no = models.CharField(
        max_length=30,
        unique=True,
        verbose_name='订单号',
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        db_index=True,
        related_name='orders',
        verbose_name='下单用户',
    )
    flight = models.ForeignKey(
        'flights.Flight',
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='航班',
    )
    cabin_class = models.ForeignKey(
        'flights.CabinClass',
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='舱位',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        db_index=True,
        default='PENDING',
        verbose_name='订单状态',
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='订单总金额',
    )
    pay_expire_at = models.DateTimeField(
        db_index=True,
        verbose_name='支付截止时间',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
    )

    class Meta:
        db_table = 'orders_order'
        verbose_name = '订单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.order_no

    def can_transition_to(self, new_status):
        allowed = self.VALID_TRANSITIONS.get(self.status, [])
        return new_status in allowed

    @classmethod
    def generate_order_no(cls):
        now = timezone.now()
        date_str = now.strftime('%Y%m%d')
        prefix = f'ORD{date_str}'
        existing_count = cls.objects.filter(order_no__startswith=prefix).count()
        seq = str(existing_count + 1).zfill(4)
        return f'{prefix}{seq}'

    @classmethod
    def create_order(cls, user, flight, cabin_class, passengers_data, addon_services_data=None):
        with transaction.atomic():
            CabinClass.decrease_available_seats(cabin_class.pk, len(passengers_data))

            ticket_price = cabin_class.base_price + cabin_class.tax + cabin_class.fuel_surcharge
            total_amount = ticket_price * len(passengers_data)

            if addon_services_data:
                for svc in addon_services_data:
                    total_amount += Decimal(str(svc.get('price', 0)))

            order = cls.objects.create(
                order_no=cls.generate_order_no(),
                user=user,
                flight=flight,
                cabin_class=cabin_class,
                total_amount=total_amount.quantize(Decimal('0.01')),
                pay_expire_at=timezone.now() + timedelta(minutes=30),
            )

            for p_data in passengers_data:
                Passenger.objects.create(
                    order=order,
                    name=p_data['name'],
                    id_type=p_data['id_type'],
                    id_number=p_data['id_number'],
                    passenger_type=p_data['passenger_type'],
                )

            if addon_services_data:
                for svc in addon_services_data:
                    AddonService.objects.create(
                        order=order,
                        service_name=svc['service_name'],
                        price=Decimal(str(svc['price'])),
                    )

        return order


class Passenger(models.Model):
    ID_TYPE_CHOICES = (
        ('ID_CARD', '身份证'),
        ('PASSPORT', '护照'),
    )
    PASSENGER_TYPE_CHOICES = (
        ('ADULT', '成人'),
        ('CHILD', '儿童'),
        ('INFANT', '婴儿'),
    )
    TICKET_STATUS_CHOICES = (
        ('NORMAL', '正常'),
        ('REFUNDING', '退票中'),
        ('REFUNDED', '已退票'),
        ('RESCHEDULED', '已改签'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        db_index=True,
        related_name='passengers',
        verbose_name='关联订单',
    )
    name = models.CharField(
        max_length=50,
        verbose_name='姓名',
    )
    id_type = models.CharField(
        max_length=20,
        choices=ID_TYPE_CHOICES,
        verbose_name='证件类型',
    )
    id_number = models.CharField(
        max_length=50,
        verbose_name='证件号',
    )
    passenger_type = models.CharField(
        max_length=10,
        choices=PASSENGER_TYPE_CHOICES,
        verbose_name='乘机人类型',
    )
    ticket_no = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name='电子票号',
    )
    status = models.CharField(
        max_length=20,
        choices=TICKET_STATUS_CHOICES,
        default='NORMAL',
        verbose_name='票状态',
    )

    class Meta:
        db_table = 'orders_passenger'
        verbose_name = '订单乘机人'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.name}({self.id_number})'


class AddonService(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='addon_services',
        verbose_name='关联订单',
    )
    service_name = models.CharField(
        max_length=100,
        verbose_name='服务名',
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='服务单价',
    )

    class Meta:
        db_table = 'orders_addon_service'
        verbose_name = '附加服务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.service_name} - ¥{self.price}'


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', '待支付'),
        ('SUCCESS', '支付成功'),
        ('FAILED', '支付失败'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    payment_no = models.CharField(
        max_length=30,
        unique=True,
        verbose_name='支付流水号',
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        db_index=True,
        related_name='payments',
        verbose_name='关联订单',
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='实际支付金额',
    )
    method = models.CharField(
        max_length=30,
        default='MOCK',
        verbose_name='支付方式',
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING',
        verbose_name='支付状态',
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='支付成功时间',
    )

    class Meta:
        db_table = 'orders_payment'
        verbose_name = '支付流水'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.payment_no