from typing import Optional, Any, TypeVar, Generic
# Define TypeVars for generic types


class CoreBaseException(Exception):
    success: bool
    message: str
    data: Optional[Any]
    error: Optional[Any]
    status_code: int = 200

    def __init__(self, message: str, data: Optional[Any] = None, error: Optional[Any] = None):
        self.success = False
        self.message = message
        self.data = data
        self.error = error
        super().__init__(message)

    def serialize(self) -> dict:
        """Method to serialize the exception to a dictionary"""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "status_code": self.status_code
        }
