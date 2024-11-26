from typing import Optional

from pydantic import BaseModel


class UserResponse(BaseModel):
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    username: Optional[str] = None
    user_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
