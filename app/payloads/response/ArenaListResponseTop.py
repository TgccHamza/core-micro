from uuid import UUID

from pydantic import BaseModel
from typing import List, Optional


class ArenaMembers(BaseModel):
    user_id: Optional[str]
    user_email: Optional[str]
    user_name: Optional[str]
    picture: Optional[str]


class ArenaListGroupUserClientResponse(BaseModel):
    user_id: Optional[str] = None
    user_email: Optional[str]
    user_name: Optional[str]
    picture: Optional[str]

class ArenaListGroupClientResponse(BaseModel):
    id: str
    name: str
    managers: List[ArenaListGroupUserClientResponse] = []

class ArenaListResponseTop(BaseModel):
    id: str
    name: str
    group: Optional[ArenaListGroupClientResponse]
    players: List[ArenaMembers] = []

