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


class UserSession(BaseModel):
    user_id: Optional[str]
    user_email: Optional[str]
    user_fullname: Optional[str]


class SessionCreateRequest(BaseModel):
    arena_id: UUID
    game_id: Optional[UUID]


class SessionCreateResponse(BaseModel):
    id: Optional[UUID]
    arena_id: Optional[UUID]
    project_id: Optional[UUID]
    period_type: Optional[PeriodType]  # You can change this to an Enum if needed
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    access_status: AccessStatus  # You can change this to an Enum if needed
    session_status: SessionStatus  # You can change this to an Enum if needed
    view_access: ViewAccess
    # project: Optional[ProjectResponse]
    # arena: Optional[ArenaResponse]
    # players: List[SessionPlayerClientResponse]

    class Config:
        orm_mode = True
