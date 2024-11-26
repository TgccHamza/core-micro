from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

from app.enums import PeriodType, AccessStatus, ViewAccess, SessionStatus, ActivationStatus


class GroupByGameUserClientResponse(BaseModel):
    id: str
    user_id: Optional[str] = ""
    user_email: Optional[str] = ""
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""


class GroupByGameSessionPlayerClientResponse(BaseModel):
    user_id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    picture: Optional[str] = None


class GroupByGameArenaSessionResponse(BaseModel):
    id: str
    period_type: Optional[PeriodType]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    access_status: Optional[AccessStatus]
    session_status: Optional[SessionStatus]
    view_access: Optional[ViewAccess]
    players: List[GroupByGameSessionPlayerClientResponse]


class GroupByGameArenaClientResponse(BaseModel):
    id: str
    name: str
    sessions: List[GroupByGameArenaSessionResponse] = []


class GroupByGameResponse(BaseModel):
    id: UUID
    name: str
    managers: List[GroupByGameUserClientResponse]
    arenas: List[GroupByGameArenaClientResponse]
