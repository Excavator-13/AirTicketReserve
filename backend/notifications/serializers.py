from rest_framework import serializers
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    related_order_id = serializers.UUIDField(
        source='related_order.id',
        read_only=True,
        default=None,
    )

    class Meta:
        model = Notification
        fields = ('id', 'title', 'content', 'related_order_id', 'is_read', 'created_at')
        read_only_fields = ('id', 'title', 'content', 'related_order_id', 'created_at')


class NotificationMarkReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('is_read',)