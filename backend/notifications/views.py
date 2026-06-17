from rest_framework import viewsets, permissions
from rest_framework.decorators import action

from common.responses import UnifiedResponse
from common.permissions import IsOwner
from notifications.models import Notification
from notifications.serializers import NotificationSerializer, NotificationMarkReadSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            is_read_val = is_read.lower() in ('true', '1', 'yes')
            qs = qs.filter(is_read=is_read_val)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return UnifiedResponse.success(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return UnifiedResponse.success(data=serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = NotificationMarkReadSerializer(
            instance, data=request.data, partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return UnifiedResponse.success(data=NotificationSerializer(instance).data)

    def create(self, request, *args, **kwargs):
        return UnifiedResponse.error(msg='不允许手动创建通知', code=403)

    def destroy(self, request, *args, **kwargs):
        return UnifiedResponse.error(msg='不允许删除通知', code=403)

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return UnifiedResponse.success(data={'unread_count': count})