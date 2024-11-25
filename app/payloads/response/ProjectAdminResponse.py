from pydantic import BaseModel
from typing import Optional
from app.enums import PlayingType, GameType


class ProjectAdminResponse(BaseModel):
    id: str
    name: Optional[str] = None
    organisation_code: Optional[str] = None
    organization_name: Optional[str] = None
    game_type: Optional[GameType] = None
    playing_type: Optional[PlayingType] = None
    slug: Optional[str] = None


