from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import (
    SendCodeView,
    RegisterView,
    LoginView,
    CodeLoginView,
    ResetPasswordView,
    FrequentPassengerViewSet,
)

router = DefaultRouter()
router.register(r'passengers', FrequentPassengerViewSet, basename='passengers')

auth_patterns = [
    path('code/', SendCodeView.as_view(), name='send-code'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('login/code/', CodeLoginView.as_view(), name='login-code'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]

urlpatterns = [
    path('auth/', include(auth_patterns)),
] + router.urls