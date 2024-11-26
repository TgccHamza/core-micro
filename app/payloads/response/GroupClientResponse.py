from datetime import datetime

from pydantic import BaseModel
from typing import  List, Optional
from uuid import UUID

from app.enums import PeriodType, AccessStatus, ViewAccess, SessionStatus, ActivationStatus


class ProjectResponse(BaseModel):
    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    db_index: Optional[str] = None
    slug: Optional[str] = None
    visibility: Optional[str] = "public"
    activation_status: Optional[ActivationStatus] = ActivationStatus.ACTIVE
    client_id: Optional[str] = None
    client_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class GroupUserClientResponse(BaseModel):
    id: str
    user_id:  Optional[str] = ""
    user_email:  Optional[str] = ""
    first_name:  Optional[str] = ""
    last_name: Optional[str] = ""

class GroupSessionPlayerClientResponse(BaseModel):
    user_id:  Optional[str] = ""
    user_email:  Optional[str] = ""
    first_name:  Optional[str] = ""
    last_name: Optional[str] = ""


class GroupArenaSessionResponse(BaseModel):
    id: str
    period_type: Optional[PeriodType]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    access_status: Optional[AccessStatus]
    session_status: Optional[SessionStatus]
    view_access: Optional[ViewAccess]
    players: List[GroupSessionPlayerClientResponse]


class GroupArenaClientResponse(BaseModel):
    id: str
    name: str
    sessions: List[GroupArenaSessionResponse] = []


class GroupClientResponse(BaseModel):
    id: UUID
    name: str
    managers: List[GroupUserClientResponse]
    arenas: List[GroupArenaClientResponse]
    games: List[ProjectResponse]
