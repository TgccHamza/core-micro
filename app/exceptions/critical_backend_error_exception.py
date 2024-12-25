from typing import Optional, Any

from app.exceptions.base_exception import CoreBaseException


class CriticalBackendErrorException(CoreBaseException):
    def __init__(self, error: Optional[Any] = None, message: str = "An unexpected error occurred"):
        super().__init__(message=message, error=error)
        self.status_code = 500
