from pydantic import BaseModel
from typing import Optional
from app.enums import ActivationStatus
from datetime import datetime

class GameUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    game_trailer_url: Optional[str] = None
    visibility: Optional[str] = "public"
    activation_status: Optional[ActivationStatus] = ActivationStatus.ACTIVE
    client_name: Optional[str] = None
    tags: Optional[str] = None
    allow_comments: Optional[bool] = True  # Allow or disable comments
    replayable: Optional[bool] = True  # Is the game replayable
    public_leaderboard: Optional[bool] = False  # Show public leaderboards
    timezone: Optional[str] = None  # Store timezone information
    restrict_playing_hours: Optional[bool] = False  # Whether playing hours are restricted
    playing_start_time: Optional[datetime] = None  # Start time if restricted
    playing_end_time: Optional[datetime] = None  # End time if restricted
