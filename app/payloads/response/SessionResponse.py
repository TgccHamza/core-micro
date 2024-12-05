from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from typing import Optional, List

from app.enums import PeriodType, AccessStatus, SessionStatus, ViewAccess, ActivationStatus, EmailStatus


class ArenaGroupUserResponse(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


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
    id: Optional[str]
    user_id: Optional[str]
    user_email: Optional[str]
    user_name: Optional[str]
    email_status: Optional[EmailStatus]
    is_game_master: Optional[bool] = False


class UserSession(BaseModel):
    user_id: Optional[str]
    user_email: Optional[str]
    user_fullname: Optional[str]


class SessionResponse(BaseModel):
    id: Optional[UUID]
    super_game_master_mail: Optional[str] = None
    super_game_master_id: Optional[str] = None
    arena_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    db_index: Optional[str] = None
    period_type: Optional[PeriodType] = None  # You can change this to an Enum if needed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    access_status: Optional[AccessStatus] = None  # You can change this to an Enum if needed
    session_status: Optional[SessionStatus] = None  # You can change this to an Enum if needed
    view_access: Optional[ViewAccess] = None
    project: Optional[ProjectResponse] = None
    arena: Optional[ArenaResponse] = None
    players: List[SessionPlayerClientResponse]

    class Config:
        orm_mode = True
