"""
アプリケーション共通例外
UseCase / Service 層で raise し、Presentation 層でハンドリングする。
"""


class AppException(Exception):
    """全例外の基底クラス"""

    def __init__(self, detail: str = "An error occurred"):
        self.detail = detail
        super().__init__(self.detail)


class NotFoundException(AppException):
    """リソースが見つからない (HTTP 404)"""

    def __init__(self, resource: str = "Resource", resource_id: str = ""):
        super().__init__(f"{resource} not found: {resource_id}")


class UnauthorizedException(AppException):
    """認証失敗 (HTTP 401)"""

    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(detail)


class ForbiddenException(AppException):
    """権限不足 (HTTP 403)"""

    def __init__(self, detail: str = "Forbidden"):
        super().__init__(detail)


class ConflictException(AppException):
    """競合 (HTTP 409)"""

    def __init__(self, detail: str = "Conflict"):
        super().__init__(detail)


class ValidationException(AppException):
    """バリデーションエラー (HTTP 422)"""

    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail)
