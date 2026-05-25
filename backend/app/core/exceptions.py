from __future__ import annotations


class AppError(Exception):
    def __init__(self, message: str, *, code: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", *, code: str = "not_found") -> None:
        super().__init__(message, code=code, status_code=404)


class ConflictError(AppError):
    def __init__(self, message: str = "Resource conflict", *, code: str = "conflict") -> None:
        super().__init__(message, code=code, status_code=409)
