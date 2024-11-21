from uuid import UUID

from pydantic import BaseModel
from typing import List

class ArenaGroupUserClientResponse(BaseModel):
    user_id: str

class ArenaGroupClientResponse(BaseModel):
    id: str
    name: str
    managers: List[ArenaGroupUserClientResponse]

class ArenaResponseTop(BaseModel):
    id: str
    name: str
    groups: List[ArenaGroupClientResponse]

