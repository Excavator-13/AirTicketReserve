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

    response = exception_handler(exc, context)
    if response is not None:
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