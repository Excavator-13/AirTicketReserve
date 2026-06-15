from django.contrib import admin

from .models import RefundRequest


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'passenger', 'refund_amount', 'fee', 'status', 'created_at')
    list_filter = ('status',)
    readonly_fields = ('id', 'created_at')
    raw_id_fields = ('order', 'passenger')