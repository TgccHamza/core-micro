from uuid import UUID

from pydantic import BaseModel
from typing import  Optional, List


class GroupManager(BaseModel):
    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    username: Optional[str] = None

class GroupInviteManagerRequest(BaseModel):
    managers: Optional[List[GroupManager]] = []
