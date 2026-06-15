from rest_framework.response import Response


class UnifiedResponse:
    @staticmethod
    def success(data=None, msg='success', code=200):
        return Response(
            data={
                'code': code,
                'msg': msg,
                'data': data,
            },
            status=code,
        )

    @staticmethod
    def error(msg='error', code=400, data=None):
        return Response(
            data={
                'code': code,
                'msg': msg,
                'data': data,
            },
            status=code,
        )