from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_read', 'related_order', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('title', 'content')
    readonly_fields = ('id', 'created_at')
    raw_id_fields = ('user', 'related_order')