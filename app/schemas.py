from pydantic import BaseModel, Field, constr
from typing import List, Optional
from uuid import UUID
from .enums import AccessStatus, PeriodType, SessionStatus, ViewAccess, ActivationStatus
from datetime import datetime


# Pydantic Models for Project
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    db_index: Optional[str] = None
    slug: str
    visibility: Optional[str] = "public"
    activation_status: Optional[ActivationStatus] = ActivationStatus.ACTIVE
    client_id: Optional[str] = None
    client_name: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    db_index: Optional[str] = None
    slug: Optional[str] = None
    visibility: Optional[str] = "public"
    activation_status: Optional[ActivationStatus] = ActivationStatus.ACTIVE
    client_name: Optional[str] = None


class ProjectResponse(ProjectCreate):
    id: str



class UserResponse(BaseModel):
    user_id: str


class GroupResponse(BaseModel):
    id: UUID
    name: str
    users: List[UserResponse]

class GameResponse(BaseModel):
    id: str
    name: str
    type: str
    project_id: str
    order: Optional[int] = 0

class SessionResponse(BaseModel):
    id: str
    game: GameResponse
    period_type: PeriodType
    start_time: datetime
    end_time: datetime
    access_status: AccessStatus
    session_status: SessionStatus
    view_access: ViewAccess
    players: List[UserResponse]

class ArenaResponse(BaseModel):
    id: str
    name: str
    sessions: List[SessionResponse]

class ArenaResponseTop(BaseModel):
    id: str
    name: str
    groups: List[GroupResponse]


# Pydantic Models for ProjectModule
class ModuleCreate(BaseModel):
    name: str
    type: str
    project_id: str
    order: Optional[int] = 0


class ModuleUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    order: Optional[int] = 0


class ModuleResponse(ModuleCreate):
    id: str


# ---------------- Group Schemas ----------------


class GroupBase(BaseModel):
    name: str


class GroupCreate(GroupBase):
    user_ids: List[UUID]
    project_ids: List[UUID]




class Group(GroupBase):
    id: UUID
    users: List[UserResponse]
    projects: List[ProjectResponse]
    arenas: List[ArenaResponse]

    class Config:
        orm_mode = True

class GroupShow(GroupBase):
    id: UUID
    users: List[UserResponse]
    projects: List[ProjectResponse]


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    user_ids: Optional[List[UUID]] = None
    project_ids: Optional[List[UUID]] = None


# ---------------- Arena Schemas ----------------

# Base schema for Arena
class ArenaBase(BaseModel):
    name: str


# Arena creation schema, allowing association with only one group upon creation
class ArenaCreate(ArenaBase):
    group_id: UUID  # Only one group is allowed on creation


# Schema for returning Arena information with associated groups
class Arena(ArenaBase):
    id: UUID

    class Config:
        orm_mode = True


# Arena update schema without group association updates
class ArenaUpdate(BaseModel):
    name: Optional[str] = None


# Schema for associating an arena with additional groups
class ArenaAssociate(BaseModel):
    group_id: UUID


# Schema for dissociating an arena from a specific group
class ArenaDisassociation(BaseModel):
    group_id: UUID


# ---------------- Session Schemas ----------------

class SessionBase(BaseModel):
    arena_id: UUID
    project_id: Optional[UUID]
    module_id: Optional[UUID]
    period_type: PeriodType  # You can change this to an Enum if needed
    start_time: datetime
    end_time: Optional[datetime]
    access_status: AccessStatus  # You can change this to an Enum if needed
    session_status: SessionStatus  # You can change this to an Enum if needed
    view_access: ViewAccess  # You can change this to an Enum if needed


class SessionCreate(SessionBase):
    user_ids: List[UUID]


class Session(SessionBase):
    id: UUID
    project: Optional[ProjectResponse]
    game: Optional[GameResponse]
    arena: Optional[ArenaResponseTop]
    players: List[UserResponse]

    class Config:
        orm_mode = True


class SessionUpdate(BaseModel):
    arena_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    module_id: Optional[UUID] = None
    period_type: Optional[PeriodType] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    access_status: Optional[AccessStatus] = None
    session_status: Optional[SessionStatus] = None
    view_access: Optional[ViewAccess] = None
    user_ids: Optional[List[UUID]] = None
