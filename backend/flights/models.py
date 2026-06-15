import uuid
from decimal import Decimal

from django.db import models, transaction


class InsufficientSeatsError(Exception):
    pass


class SeatsExceedTotalError(Exception):
    pass


class Airport(models.Model):
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='机场IATA代码',
    )
    name = models.CharField(
        max_length=100,
        verbose_name='机场名称',
    )
    city = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name='所在城市',
    )

    class Meta:
        db_table = 'flights_airport'
        verbose_name = '机场'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.code} - {self.name}'


class Flight(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    flight_no = models.CharField(
        max_length=20,
        verbose_name='航班号',
    )
    airline = models.CharField(
        max_length=50,
        verbose_name='航空公司',
    )
    departure_airport = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name='departures',
        verbose_name='出发机场',
    )
    arrival_airport = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name='arrivals',
        verbose_name='到达机场',
    )
    departure_time = models.DateTimeField(
        db_index=True,
        verbose_name='起飞时间',
    )
    arrival_time = models.DateTimeField(
        verbose_name='降落时间',
    )
    aircraft_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='机型',
    )
    is_direct = models.BooleanField(
        default=True,
        verbose_name='是否直飞',
    )
    stop_info = models.JSONField(
        null=True,
        blank=True,
        verbose_name='经停信息',
    )

    class Meta:
        db_table = 'flights_flight'
        verbose_name = '航班'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.flight_no} ({self.departure_airport.code}->{self.arrival_airport.code})'


class CabinClass(models.Model):
    CLASS_TYPE_CHOICES = (
        ('ECONOMY', '经济舱'),
        ('BUSINESS', '商务舱'),
        ('FIRST', '头等舱'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        db_index=True,
        related_name='cabin_classes',
        verbose_name='关联航班',
    )
    class_type = models.CharField(
        max_length=20,
        choices=CLASS_TYPE_CHOICES,
        verbose_name='舱位类型',
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='基础票价',
    )
    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='税费',
    )
    fuel_surcharge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='燃油附加费',
    )
    total_seats = models.IntegerField(
        verbose_name='总座位数',
    )
    available_seats = models.IntegerField(
        verbose_name='可用座位数',
    )
    baggage_allowance = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='免费行李额',
    )
    refund_rules = models.JSONField(
        default=list,
        verbose_name='退票手续费阶梯',
    )
    reschedule_rules = models.JSONField(
        default=list,
        verbose_name='改签手续费规则',
    )

    class Meta:
        db_table = 'flights_cabin_class'
        verbose_name = '舱位与库存'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.flight.flight_no} - {self.get_class_type_display()}'

    @classmethod
    def decrease_available_seats(cls, cabin_class_id, seat_count):
        with transaction.atomic():
            cabin = cls.objects.select_for_update().get(pk=cabin_class_id)
            if cabin.available_seats < seat_count:
                raise InsufficientSeatsError(
                    f'库存不足：可用 {cabin.available_seats}，请求 {seat_count}'
                )
            cabin.available_seats -= seat_count
            cabin.save(update_fields=['available_seats'])
        return cabin

    @classmethod
    def increase_available_seats(cls, cabin_class_id, seat_count):
        with transaction.atomic():
            cabin = cls.objects.select_for_update().get(pk=cabin_class_id)
            if cabin.available_seats + seat_count > cabin.total_seats:
                raise SeatsExceedTotalError(
                    f'回滚超过总座位数：当前 {cabin.available_seats}，回滚 {seat_count}，总座位 {cabin.total_seats}'
                )
            cabin.available_seats += seat_count
            cabin.save(update_fields=['available_seats'])
        return cabin

    def calculate_refund_fee(self, hours_before_departure):
        if not self.refund_rules:
            return Decimal('0.00')

        sorted_rules = sorted(
            self.refund_rules,
            key=lambda r: r.get('hours_before', 0),
            reverse=True,
        )

        for rule in sorted_rules:
            if hours_before_departure >= rule.get('hours_before', 0):
                fee_rate = Decimal(str(rule.get('fee_rate', 0)))
                return (self.base_price * fee_rate).quantize(Decimal('0.01'))

        strictest_rate = Decimal(str(sorted_rules[0].get('fee_rate', 0)))
        return (self.base_price * strictest_rate).quantize(Decimal('0.01'))

    def calculate_reschedule_fee(self, hours_before_departure):
        if not self.reschedule_rules:
            return Decimal('0.00')

        sorted_rules = sorted(
            self.reschedule_rules,
            key=lambda r: r.get('hours_before', 0),
            reverse=True,
        )

        for rule in sorted_rules:
            if hours_before_departure >= rule.get('hours_before', 0):
                fee_rate = Decimal(str(rule.get('fee_rate', 0)))
                return (self.base_price * fee_rate).quantize(Decimal('0.01'))

        strictest_rate = Decimal(str(sorted_rules[0].get('fee_rate', 0)))
        return (self.base_price * strictest_rate).quantize(Decimal('0.01'))