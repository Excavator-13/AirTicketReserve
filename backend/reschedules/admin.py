from django.contrib import admin

from .models import RescheduleRequest


@admin.register(RescheduleRequest)
class RescheduleRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'passenger', 'new_flight', 'new_cabin', 'price_difference', 'fee', 'status')
    list_filter = ('status',)
    readonly_fields = ('id',)
    raw_id_fields = ('order', 'passenger', 'new_flight', 'new_cabin')