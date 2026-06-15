from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView


@api_view(['GET'])
def health_check(request):
    return Response({'code': 200, 'msg': 'success', 'data': {'status': 'ok'}})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', health_check),
    path('api/v1/', include('users.urls')),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/v1/', include('flights.urls')),
    path('api/v1/', include('orders.urls')),
    path('api/v1/', include('notifications.urls')),
]