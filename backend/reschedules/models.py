import uuid

from django.db import models


class RescheduleRequest(models.Model):
    RESCHEDULE_STATUS_CHOICES = (
        ('PENDING', '待处理'),
        ('PAID', '已支付差价'),
        ('COMPLETED', '已完成'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='reschedule_requests',
        verbose_name='原订单',
    )
    passenger = models.ForeignKey(
        'orders.Passenger',
        on_delete=models.CASCADE,
        related_name='reschedule_requests',
        verbose_name='原乘机人',
    )
    new_flight = models.ForeignKey(
        'flights.Flight',
        on_delete=models.PROTECT,
        related_name='reschedule_requests',
        verbose_name='新航班',
    )
    new_cabin = models.ForeignKey(
        'flights.CabinClass',
        on_delete=models.PROTECT,
        related_name='reschedule_requests',
        verbose_name='新舱位',
    )
    price_difference = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='差价',
        help_text='正数为补交，负数为退还',
    )
    fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='改签手续费',
    )
    status = models.CharField(
        max_length=20,
        choices=RESCHEDULE_STATUS_CHOICES,
        default='PENDING',
        verbose_name='改签状态',
    )

    class Meta:
        db_table = 'reschedules_reschedule_request'
        verbose_name = '改签申请'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'改签申请 {self.id} - {self.get_status_display()}'