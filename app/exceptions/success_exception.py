from typing import Optional, Any
from app.exceptions.base_exception import CoreBaseException


# SuccessException also inherits from CoreBaseException with generics
class SuccessException(CoreBaseException):
    def __init__(self, data: Optional[Any] = None, message: str = "Request processed successfully"):
        super().__init__(message, data)
        self.status_code = 200
        self.success = True
