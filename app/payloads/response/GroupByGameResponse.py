from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

from app.enums import PeriodType, AccessStatus, ViewAccess, SessionStatus, ActivationStatus


class GroupByGameUserClientResponse(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = ""
    user_email: Optional[str] = ""
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""

class GroupByGameArenaClientResponse(BaseModel):
    id: str
    name: str


class GroupByGameResponse(BaseModel):
    id: UUID
    name: str
    managers: List[GroupByGameUserClientResponse]
    arenas: List[GroupByGameArenaClientResponse]
