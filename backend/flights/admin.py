from django.contrib import admin

from .models import Airport, CabinClass, Flight


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'city')
    search_fields = ('code', 'name', 'city')


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_no', 'airline', 'departure_airport', 'arrival_airport', 'departure_time', 'arrival_time', 'is_direct')
    list_filter = ('airline', 'is_direct')
    search_fields = ('flight_no', 'airline')
    readonly_fields = ('id',)
    raw_id_fields = ('departure_airport', 'arrival_airport')
    date_hierarchy = 'departure_time'


@admin.register(CabinClass)
class CabinClassAdmin(admin.ModelAdmin):
    list_display = ('flight', 'class_type', 'base_price', 'total_seats', 'available_seats')
    list_filter = ('class_type',)
    readonly_fields = ('id',)
    raw_id_fields = ('flight',)