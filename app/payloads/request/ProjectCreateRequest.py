from pydantic import BaseModel
from typing import Optional
from app.enums import ActivationStatus, GameType, PlayingType
from datetime import datetime, timedelta


# Pydantic Models for Project
class ProjectCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    db_index: Optional[str] = None
    slug: str
    visibility: Optional[str] = "public"
    game_type: Optional[GameType] = GameType.DIGITAL
    playing_type: Optional[PlayingType] = PlayingType.SOLO
    activation_status: Optional[ActivationStatus] = ActivationStatus.ACTIVE
    organisation_code: Optional[str] = None
    client_id: Optional[str] = None
    client_name: Optional[str] = None
    start_time: Optional[datetime] = datetime.now() + timedelta(days=30)
    end_time: Optional[datetime] = datetime.now() + timedelta(days=60)
    tags: Optional[str] = ""
