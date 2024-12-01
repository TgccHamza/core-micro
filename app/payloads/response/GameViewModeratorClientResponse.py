from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List
from app.enums import GameType, PlayingType, PeriodType, AccessStatus, SessionStatus, ViewAccess
from datetime import datetime


class GameViewModeratorSessionPlayerClientResponse(BaseModel):
    user_id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    picture: Optional[str] = None


class GameViewModeratorArenaResponse(BaseModel):
    id: str
    name: str


class GameViewModeratorSessionResponse(BaseModel):
    id: Optional[UUID]
    arena: Optional[GameViewModeratorArenaResponse]
    period_type: Optional[PeriodType]  # You can change this to an Enum if needed
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    access_status: AccessStatus  # You can change this to an Enum if needed
    session_status: SessionStatus  # You can change this to an Enum if needed
    view_access: ViewAccess
    players: List[GameViewModeratorSessionPlayerClientResponse]


class GameViewModeratorClientResponse(BaseModel):
    id: str
    role: Optional[str] = 'moderator'
    game_name: Optional[str] = None
    client_name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None
    online_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    game_type: Optional[GameType] = None
    playing_type: Optional[PlayingType] = None
    sessions: List[GameViewModeratorSessionResponse] = []
    tags: List[str] = []
