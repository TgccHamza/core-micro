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

class ModuleResponse(BaseModel):
    id: str
    name: str
    type: str
    project_id: str
    order: Optional[int] = 0


class GroupUserClientResponse(BaseModel):
    user_id: str

class GroupSessionPlayerClientResponse(BaseModel):
    user_id: str
    module: Optional[ModuleResponse]


class GroupArenaSessionResponse(BaseModel):
    id: str
    period_type: PeriodType
    start_time: datetime
    end_time: datetime
    access_status: AccessStatus
    session_status: SessionStatus
    view_access: ViewAccess
    players: List[GroupSessionPlayerClientResponse]


class GroupArenaClientResponse(BaseModel):
    id: str
    name: str


class GroupClientResponse(BaseModel):
    id: UUID
    name: str
    managers: List[GroupUserClientResponse]
    arenas: List[GroupArenaClientResponse]
    games: List[ProjectResponse]
