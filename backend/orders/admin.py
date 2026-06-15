from django.contrib import admin

from .models import AddonService, Order, Passenger, Payment


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_no', 'user', 'flight', 'cabin_class', 'status', 'total_amount', 'pay_expire_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('order_no',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    raw_id_fields = ('user', 'flight', 'cabin_class')
    date_hierarchy = 'created_at'


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'id_type', 'id_number', 'passenger_type', 'ticket_no', 'status')
    list_filter = ('id_type', 'passenger_type', 'status')
    search_fields = ('name', 'id_number')
    readonly_fields = ('id',)
    raw_id_fields = ('order',)


@admin.register(AddonService)
class AddonServiceAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'order', 'price')
    readonly_fields = ('id',)
    raw_id_fields = ('order',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_no', 'order', 'amount', 'method', 'status', 'paid_at')
    list_filter = ('status', 'method')
    search_fields = ('payment_no',)
    readonly_fields = ('id',)
    raw_id_fields = ('order',)