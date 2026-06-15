import uuid

from django.db import models


class Notification(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        db_index=True,
        related_name='notifications',
        verbose_name='接收用户',
    )
    title = models.CharField(
        max_length=200,
        verbose_name='通知标题',
    )
    content = models.TextField(
        verbose_name='通知内容',
    )
    related_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='关联订单',
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='是否已读',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
    )

    class Meta:
        db_table = 'notifications_notification'
        verbose_name = '站内通知'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.user.username}'