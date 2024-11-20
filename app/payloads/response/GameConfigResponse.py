from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.enums import ActivationStatus, GameType, PlayingType


# Schema
class GameConfigResponse(BaseModel):
    id: Optional[str]
    name: Optional[str]
    description: Optional[str]
    game_trailer_url: Optional[str]
    slug: Optional[str]
    visibility: Optional[str]
    activation_status: Optional[ActivationStatus]
    game_type: Optional[GameType]
    playing_type: Optional[PlayingType]
    client_name: Optional[str]
    tags: Optional[str]
    allow_comments: Optional[bool]
    replayable: Optional[bool]
    public_leaderboard: Optional[bool]
    timezone: Optional[str]
    restrict_playing_hours: Optional[bool]
    playing_start_time: Optional[datetime]
    playing_end_time: Optional[datetime]
    class Config:
        orm_mode = True
