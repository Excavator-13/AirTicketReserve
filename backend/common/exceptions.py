from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
)
from django.http import Http404
from rest_framework.response import Response

from common.business_exceptions import (
    ConflictError,
    BusinessValidationError,
    AccountLockedError,
    RateLimitError,
)


def unified_exception_handler(exc, context):
    if isinstance(exc, ValidationError):
        return Response(
            data={
                'code': 400,
                'msg': '请求参数错误',
                'data': exc.detail,
            },
            status=400,
        )

    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        return Response(
            data={
                'code': 401,
                'msg': '未授权',
                'data': None,
            },
            status=401,
        )

    if isinstance(exc, PermissionDenied):
        return Response(
            data={
                'code': 403,
                'msg': '禁止访问',
                'data': None,
            },
            status=403,
        )

    if isinstance(exc, (NotFound, Http404)):
        return Response(
            data={
                'code': 404,
                'msg': '资源不存在',
                'data': None,
            },
            status=404,
        )

    if isinstance(exc, ConflictError):
        return Response(
            data={
                'code': 409,
                'msg': str(exc.detail) if exc.detail else '资源冲突',
                'data': exc.data,
            },
            status=409,
        )

    if isinstance(exc, BusinessValidationError):
        return Response(
            data={
                'code': 422,
                'msg': str(exc.detail) if exc.detail else '业务规则校验失败',
                'data': exc.data,
            },
            status=422,
        )

    if isinstance(exc, AccountLockedError):
        return Response(
            data={
                'code': 423,
                'msg': str(exc.detail) if exc.detail else '账号已锁定',
                'data': exc.data,
            },
            status=423,
        )

    if isinstance(exc, RateLimitError):
        return Response(
            data={
                'code': 429,
                'msg': str(exc.detail) if exc.detail else '请求过于频繁',
                'data': exc.data,
            },
            status=429,
        )

    response = exception_handler(exc, context)
    if response is not None:
        if isinstance(response.data, dict) and 'code' in response.data and 'msg' in response.data:
            return response
        return Response(
            data={
                'code': response.status_code,
                'msg': str(exc) if exc else 'error',
                'data': None,
            },
            status=response.status_code,
        )

    return Response(
        data={
            'code': 500,
            'msg': '服务器内部错误',
            'data': None,
        },
        status=500,
    )