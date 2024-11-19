from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from typing import Optional, List

from app.enums import PeriodType, AccessStatus, SessionStatus, ViewAccess, ActivationStatus


class ArenaGroupUserResponse(BaseModel):
    user_id: str

class ArenaGroupResponse(BaseModel):
    id: str
    name: str
    managers: List[ArenaGroupUserResponse]

class ArenaResponse(BaseModel):
    id: str
    name: str
    groups: List[ArenaGroupResponse]

class ModuleResponse(BaseModel):
    id: str
    name: str
    type: str
    project_id: str
    order: Optional[int] = 0


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
    start_time: Optional[datetime]
    end_time: Optional[datetime]


class SessionPlayerClientResponse(BaseModel):
    user_id: str
    module: Optional[ModuleResponse]

class SessionCreateRequest(BaseModel):
    arena_id: UUID
    project_id: Optional[UUID]
    period_type: PeriodType  # You can change this to an Enum if needed
    start_time: datetime
    end_time: Optional[datetime]
    access_status: AccessStatus  # You can change this to an Enum if needed
    session_status: SessionStatus  # You can change this to an Enum if needed
    view_access: ViewAccess  # You can change this to an Enum if needed
    user_ids: List[UUID]

class SessionResponse(BaseModel):
    id: Optional[UUID]
    arena_id: Optional[UUID]
    project_id: Optional[UUID]
    period_type: Optional[PeriodType]  # You can change this to an Enum if needed
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    access_status: AccessStatus  # You can change this to an Enum if needed
    session_status: SessionStatus  # You can change this to an Enum if needed
    view_access: ViewAccess
    project: Optional[ProjectResponse]
    arena: Optional[ArenaResponse]
    players: List[SessionPlayerClientResponse]

    class Config:
        orm_mode = True
