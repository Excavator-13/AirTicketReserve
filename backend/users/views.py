import time

from rest_framework.views import APIView
from rest_framework import permissions, viewsets
from rest_framework_simplejwt.tokens import RefreshToken

from common.responses import UnifiedResponse
from common.business_exceptions import RateLimitError
from users.models import User, FrequentPassenger
from users.serializers import (
    RegisterSerializer,
    LoginSerializer,
    CodeLoginSerializer,
    ResetPasswordSerializer,
    UserSerializer,
    FrequentPassengerSerializer,
)

_code_send_timestamps = {}


class SendCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get('phone')
        email = request.data.get('email')

        if not phone and not email:
            return UnifiedResponse.error(msg='手机号和邮箱至少填写一项', code=400)

        key = phone or email
        now = time.time()
        last_sent = _code_send_timestamps.get(key, 0)
        if now - last_sent < 60:
            remaining = int(60 - (now - last_sent))
            raise RateLimitError(
                detail=f'请{remaining}秒后再试',
                data={'remaining_seconds': remaining},
            )

        _code_send_timestamps[key] = now
        code = '123456'
        print(f'[验证码] {key} => {code}')

        return UnifiedResponse.success(data=None, msg='验证码发送成功')


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return UnifiedResponse.success(
            data={
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            msg='注册成功',
            code=201,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        return UnifiedResponse.success(
            data={
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            msg='登录成功',
        )


class CodeLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CodeLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        return UnifiedResponse.success(
            data={
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            msg='登录成功',
        )


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        new_password = serializer.validated_data['new_password']

        user.set_password(new_password)
        user.password_reset_token = None
        user.save()

        return UnifiedResponse.success(data=None, msg='密码重置成功')


class FrequentPassengerViewSet(viewsets.ModelViewSet):
    serializer_class = FrequentPassengerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FrequentPassenger.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return UnifiedResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return UnifiedResponse.success(data=serializer.data, code=201)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return UnifiedResponse.success(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return UnifiedResponse.success(data=None)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return UnifiedResponse.success(data=serializer.data)