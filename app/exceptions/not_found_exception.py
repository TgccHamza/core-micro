from typing import Optional, Any

from app.exceptions.base_exception import CoreBaseException


class NotFoundException(CoreBaseException):
    def __init__(self, error: Optional[Any] = None, message: str = "Item not found"):
        super().__init__(message=message, error=error)
        self.status_code = 404