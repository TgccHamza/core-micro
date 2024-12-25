from typing import Optional, Any

from app.exceptions.base_exception import CoreBaseException


class ForbiddenAccessException(CoreBaseException):
    def __init__(self, message: str = "Forbidden access", error: Optional[Any] = None):
        super().__init__(message=message, error=error)
        self.status_code = 403
