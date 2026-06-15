import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name='手机号',
        help_text='手机号，登录标识之一',
    )
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        verbose_name='邮箱',
        help_text='邮箱，登录标识之一',
    )
    is_locked = models.BooleanField(
        default=False,
        verbose_name='是否锁定',
        help_text='账号是否锁定（连续错误5次）',
    )
    lock_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='锁定解除时间',
        help_text='锁定解除时间',
    )
    password_reset_token = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name='重置密码Token',
        help_text='模拟重置密码的临时Token',
    )

    class Meta:
        db_table = 'users_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class FrequentPassenger(models.Model):
    ID_TYPE_CHOICES = (
        ('ID_CARD', '身份证'),
        ('PASSPORT', '护照'),
    )
    PASSENGER_TYPE_CHOICES = (
        ('ADULT', '成人'),
        ('CHILD', '儿童'),
        ('INFANT', '婴儿'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='frequent_passengers',
        verbose_name='关联用户',
    )
    name = models.CharField(
        max_length=50,
        verbose_name='乘机人姓名',
    )
    id_type = models.CharField(
        max_length=20,
        choices=ID_TYPE_CHOICES,
        verbose_name='证件类型',
    )
    id_number = models.CharField(
        max_length=50,
        verbose_name='证件号码',
    )
    passenger_type = models.CharField(
        max_length=10,
        choices=PASSENGER_TYPE_CHOICES,
        verbose_name='乘机人类型',
    )

    class Meta:
        db_table = 'users_frequent_passenger'
        verbose_name = '常用乘机人'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.name}({self.get_id_type_display()})'