from rest_framework.exceptions import APIException


class ConflictError(APIException):
    status_code = 409
    default_detail = '资源冲突'
    default_code = 'conflict'

    def __init__(self, detail=None, data=None):
        self.data = data
        super().__init__(detail)


class BusinessValidationError(APIException):
    status_code = 422
    default_detail = '业务规则校验失败'
    default_code = 'business_validation_error'

    def __init__(self, detail=None, data=None):
        self.data = data
        super().__init__(detail)


class AccountLockedError(APIException):
    status_code = 423
    default_detail = '账号已锁定'
    default_code = 'account_locked'

    def __init__(self, detail=None, data=None):
        self.data = data
        super().__init__(detail)


class RateLimitError(APIException):
    status_code = 429
    default_detail = '请求过于频繁'
    default_code = 'rate_limit'

    def __init__(self, detail=None, data=None):
        self.data = data
        super().__init__(detail)