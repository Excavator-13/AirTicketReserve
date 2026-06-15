from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import FrequentPassenger, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'phone', 'email', 'is_locked', 'lock_until', 'is_active', 'date_joined')
    list_filter = ('is_locked', 'is_active')
    search_fields = ('username', 'phone', 'email')
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {
            'fields': ('phone', 'is_locked', 'lock_until', 'password_reset_token'),
        }),
    )


@admin.register(FrequentPassenger)
class FrequentPassengerAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'id_type', 'id_number', 'passenger_type')
    list_filter = ('id_type', 'passenger_type')
    search_fields = ('name', 'id_number')
    readonly_fields = ('id',)
    raw_id_fields = ('user',)