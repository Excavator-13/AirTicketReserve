from django.contrib import admin
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def health_check(request):
    return Response({'code': 200, 'msg': 'success', 'data': {'status': 'ok'}})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', health_check),
]
