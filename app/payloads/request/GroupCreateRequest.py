from uuid import UUID

from pydantic import BaseModel
from typing import  Optional, List


class GroupCreateRequest(BaseModel):
    name: str
    user_ids: Optional[List[UUID]] = []
    project_ids: List[UUID]
