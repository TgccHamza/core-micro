from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from typing import List, Optional

from app.enums import PeriodType, AccessStatus, SessionStatus, ViewAccess


class ArenaShowByGameSessionMemberResponse(BaseModel):
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    picture: Optional[str] = None


class ArenaShowByGameSessionResponse(BaseModel):
    id: str
    period_type: Optional[PeriodType] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    access_status: Optional[AccessStatus] = None
    session_status: Optional[SessionStatus] = None
    view_access: Optional[ViewAccess] = None
    players: List[ArenaShowByGameSessionMemberResponse] = []


class ArenaShowByGameResponse(BaseModel):
    id: str
    name: str
    sessions: List[ArenaShowByGameSessionResponse]
