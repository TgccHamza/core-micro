from typing import Optional, Generic, TypeVar, Any

from pydantic import BaseModel

# Define TypeVars for generic types
TData = TypeVar('TData')  # For the 'data' type


# SuccessException also inherits from CoreBaseException with generics
class SuccessResponse(BaseModel, Generic[TData]):
    success: bool = True
    message: str
    data: Optional[TData]
    error: Optional[Any]
    status_code: int = 200

    def __init__(self, message: str = "Request processed successfully", data: Optional[TData] = None,
                 error: Optional[Any] = None):
        super().__init__(status_code=200,
                         success=True, message=message, data=data,
                         error=None)
        self.status_code = 200
        self.success = True
        self.message = message
        self.data = data
        self.error = error

    def serialize(self) -> dict:
        """Method to serialize the exception to a dictionary"""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error": self.error
        }
