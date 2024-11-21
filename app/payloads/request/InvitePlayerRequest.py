from uuid import UUID

from pydantic import BaseModel
from typing import Optional, List


class UserSession(BaseModel):
    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    user_fullname: Optional[str] = None

class InvitePlayerRequest(BaseModel):
    members: Optional[List[UserSession]] = []