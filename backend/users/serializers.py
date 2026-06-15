import re
from datetime import timedelta

from rest_framework import serializers
from django.utils import timezone

from users.models import User, FrequentPassenger


class RegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(required=False, max_length=20)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, max_length=128)
    code = serializers.CharField(write_only=True, max_length=6)

    def validate(self, attrs):
        phone = attrs.get('phone')
        email = attrs.get('email')

        if not phone and not email:
            raise serializers.ValidationError('手机号和邮箱至少填写一项')

        if phone:
            if not re.match(r'^1[3-9]\d{9}$', phone):
                raise serializers.ValidationError('手机号格式不正确')
            if User.objects.filter(phone=phone).exists():
                raise serializers.ValidationError('该手机号已注册')

        if email:
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError('该邮箱已注册')

        code = attrs.get('code')
        if code != '123456':
            raise serializers.ValidationError('验证码错误')

        password = attrs.get('password')
        if len(password) < 8:
            raise serializers.ValidationError('密码长度至少8位')
        if not re.search(r'[a-zA-Z]', password):
            raise serializers.ValidationError('密码必须包含字母')
        if not re.search(r'\d', password):
            raise serializers.ValidationError('密码必须包含数字')

        return attrs

    def create(self, validated_data):
        phone = validated_data.pop('phone', None)
        email = validated_data.pop('email', None)
        password = validated_data.pop('password')
        validated_data.pop('code')

        username = phone or email
        user = User.objects.create_user(
            username=username,
            phone=phone,
            email=email,
            password=password,
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        try:
            if re.match(r'^1[3-9]\d{9}$', username):
                user = User.objects.get(phone=username)
            elif '@' in username:
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError('用户名或密码错误')

        if user.is_locked and user.lock_until and user.lock_until > timezone.now():
            remaining = int((user.lock_until - timezone.now()).total_seconds() / 60)
            from common.business_exceptions import AccountLockedError
            raise AccountLockedError(
                detail=f'账号已锁定，请{remaining}分钟后再试',
                data={'lock_until': user.lock_until.isoformat()},
            )

        if user.is_locked and user.lock_until and user.lock_until <= timezone.now():
            user.is_locked = False
            user.login_fail_count = 0
            user.lock_until = None
            user.save(update_fields=['is_locked', 'login_fail_count', 'lock_until'])

        if not user.check_password(password):
            user.login_fail_count += 1
            if user.login_fail_count >= 5:
                user.is_locked = True
                user.lock_until = timezone.now() + timedelta(minutes=30)
                user.save(update_fields=['is_locked', 'lock_until', 'login_fail_count'])
                from common.business_exceptions import AccountLockedError
                raise AccountLockedError(
                    detail='密码错误次数过多，账号已锁定30分钟',
                    data={'lock_until': user.lock_until.isoformat()},
                )
            user.save(update_fields=['login_fail_count'])
            raise serializers.ValidationError('用户名或密码错误')

        user.login_fail_count = 0
        user.save(update_fields=['login_fail_count'])

        attrs['user'] = user
        return attrs


class CodeLoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        phone = attrs.get('phone')
        code = attrs.get('code')

        if code != '123456':
            raise serializers.ValidationError('验证码错误')

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError('该手机号未注册')

        if user.is_locked and user.lock_until and user.lock_until > timezone.now():
            remaining = int((user.lock_until - timezone.now()).total_seconds() / 60)
            from common.business_exceptions import AccountLockedError
            raise AccountLockedError(
                detail=f'账号已锁定，请{remaining}分钟后再试',
                data={'lock_until': user.lock_until.isoformat()},
            )

        if user.is_locked and user.lock_until and user.lock_until <= timezone.now():
            user.is_locked = False
            user.login_fail_count = 0
            user.lock_until = None
            user.save(update_fields=['is_locked', 'login_fail_count', 'lock_until'])

        attrs['user'] = user
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(required=False, max_length=20)
    email = serializers.EmailField(required=False)
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(max_length=128)

    def validate(self, attrs):
        phone = attrs.get('phone')
        email = attrs.get('email')

        if not phone and not email:
            raise serializers.ValidationError('手机号和邮箱至少填写一项')

        code = attrs.get('code')
        if code != '123456':
            raise serializers.ValidationError('验证码错误')

        new_password = attrs.get('new_password')
        if len(new_password) < 8:
            raise serializers.ValidationError('密码长度至少8位')
        if not re.search(r'[a-zA-Z]', new_password):
            raise serializers.ValidationError('密码必须包含字母')
        if not re.search(r'\d', new_password):
            raise serializers.ValidationError('密码必须包含数字')

        try:
            if phone:
                user = User.objects.get(phone=phone)
            else:
                user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('该账号不存在')

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'phone', 'email', 'is_locked', 'date_joined')
        read_only_fields = fields


class FrequentPassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrequentPassenger
        fields = ('id', 'name', 'id_type', 'id_number', 'passenger_type')
        read_only_fields = ('id',)

    def validate(self, attrs):
        id_type = attrs.get('id_type', '')
        id_number = attrs.get('id_number', '')
        if id_type == 'ID_CARD':
            if not re.match(r'^\d{17}[\dXx]$', id_number):
                raise serializers.ValidationError({'id_number': '身份证号格式不正确'})
        elif id_type == 'PASSPORT':
            if not re.match(r'^[A-Za-z0-9]{5,20}$', id_number):
                raise serializers.ValidationError({'id_number': '护照号格式不正确'})
        return attrs