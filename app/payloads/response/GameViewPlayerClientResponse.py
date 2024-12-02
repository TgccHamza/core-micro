from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List
from app.enums import GameType, PlayingType, PeriodType, AccessStatus, SessionStatus, ViewAccess
from datetime import datetime


class GameViewPlayerArenaResponse(BaseModel):
    id: str
    name: str

class PlayerModuleLinkResponse(BaseModel):
    name: Optional[str]
    template_code: Optional[str]

class GameViewPlayerSessionResponse(BaseModel):
    id: Optional[UUID]
    arena: Optional[GameViewPlayerArenaResponse] = None
    period_type: Optional[PeriodType]  # You can change this to an Enum if needed
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    db_index: Optional[str]
    access_status: Optional[AccessStatus]  # You can change this to an Enum if needed
    session_status: Optional[SessionStatus]  # You can change this to an Enum if needed
    view_access: Optional[ViewAccess]
    is_game_master: Optional[bool] = False
    links: List[PlayerModuleLinkResponse]


class GameViewPlayerClientResponse(BaseModel):
    id: str
    role: Optional[str] = 'player'
    game_name: Optional[str] = None
    client_name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None
    online_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    game_type: Optional[GameType] = None
    playing_type: Optional[PlayingType] = None
    sessions: List[GameViewPlayerSessionResponse] = []
    tags: List[str] = []
