from uuid import UUID

from pydantic import BaseModel
from typing import  Optional, List


class GroupManager(BaseModel):
    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class GroupCreateRequest(BaseModel):
    name: str
    managers: Optional[List[GroupManager]] = []
    project_ids: List[UUID]
