from datetime import datetime

from pydantic import BaseModel
from typing import  List, Optional
from uuid import UUID

from app.enums import ActivationStatus


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

class GroupListUserClientResponse(BaseModel):
    id: str
    user_id:  Optional[str] = ""
    user_email:  Optional[str] = ""
    first_name:  Optional[str] = ""
    last_name: Optional[str] = ""



class GroupListArenaClientResponse(BaseModel):
    id: str
    name: str


class GroupListClientResponse(BaseModel):
    id: UUID
    name: str
    managers: List[GroupListUserClientResponse]
    arenas: List[GroupListArenaClientResponse]
    games: List[ProjectResponse]