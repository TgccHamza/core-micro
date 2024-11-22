from uuid import UUID

from pydantic import BaseModel
from typing import  List


class GroupUpdateRequest(BaseModel):
    name: str
    project_ids: List[UUID]
