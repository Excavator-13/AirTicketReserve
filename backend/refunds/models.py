import uuid

from django.db import models


class RefundRequest(models.Model):
    REFUND_STATUS_CHOICES = (
        ('PENDING', '待审核'),
        ('APPROVED', '已通过'),
        ('REJECTED', '已拒绝'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='refund_requests',
        verbose_name='关联订单',
    )
    passenger = models.ForeignKey(
        'orders.Passenger',
        on_delete=models.CASCADE,
        related_name='refund_requests',
        verbose_name='关联乘机人',
    )
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='预计退款金额',
    )
    fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='手续费',
    )
    status = models.CharField(
        max_length=20,
        choices=REFUND_STATUS_CHOICES,
        default='PENDING',
        verbose_name='审核状态',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='申请时间',
    )

    class Meta:
        db_table = 'refunds_refund_request'
        verbose_name = '退票申请'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'退票申请 {self.id} - {self.get_status_display()}'