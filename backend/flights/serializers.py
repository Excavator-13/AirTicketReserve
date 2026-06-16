from rest_framework import serializers
from flights.models import Airport, Flight, CabinClass


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ('code', 'name', 'city')


class CabinClassListSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        source='base_price',
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CabinClass
        fields = ('id', 'class_type', 'price', 'tax', 'fuel_surcharge', 'available_seats')


class CabinClassDetailSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        source='base_price',
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CabinClass
        fields = (
            'id', 'class_type', 'base_price', 'price', 'tax',
            'fuel_surcharge', 'available_seats', 'baggage_allowance',
            'refund_rules', 'reschedule_rules',
        )


class FlightListSerializer(serializers.ModelSerializer):
    departure_airport = AirportSerializer(read_only=True)
    arrival_airport = AirportSerializer(read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    cabins = CabinClassListSerializer(source='cabin_classes', many=True, read_only=True)
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = (
            'id', 'flight_no', 'airline',
            'departure_airport', 'arrival_airport',
            'departure_time', 'arrival_time',
            'duration_minutes', 'is_direct', 'aircraft_type', 'min_price', 'cabins',
        )

    def get_duration_minutes(self, obj):
        if obj.departure_time and obj.arrival_time:
            delta = obj.arrival_time - obj.departure_time
            return int(delta.total_seconds() / 60)
        return None

    def get_min_price(self, obj):
        cabins = obj.cabin_classes.all()
        if not cabins:
            return None
        from decimal import Decimal
        prices = []
        for c in cabins:
            prices.append(c.base_price + c.tax + c.fuel_surcharge)
        return min(prices)


class FlightDetailSerializer(serializers.ModelSerializer):
    departure_airport = AirportSerializer(read_only=True)
    arrival_airport = AirportSerializer(read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    cabins = CabinClassDetailSerializer(source='cabin_classes', many=True, read_only=True)
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = (
            'id', 'flight_no', 'airline',
            'departure_airport', 'arrival_airport',
            'departure_time', 'arrival_time',
            'duration_minutes', 'is_direct', 'stop_info',
            'aircraft_type', 'min_price', 'cabins',
        )

    def get_duration_minutes(self, obj):
        if obj.departure_time and obj.arrival_time:
            delta = obj.arrival_time - obj.departure_time
            return int(delta.total_seconds() / 60)
        return None

    def get_min_price(self, obj):
        cabins = obj.cabin_classes.all()
        if not cabins:
            return None
        from decimal import Decimal
        prices = []
        for c in cabins:
            prices.append(c.base_price + c.tax + c.fuel_surcharge)
        return min(prices)