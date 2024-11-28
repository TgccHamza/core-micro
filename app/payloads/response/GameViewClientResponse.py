from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List
from app.enums import GameType, PlayingType, PeriodType, AccessStatus, SessionStatus, ViewAccess
from datetime import datetime

class GameViewSessionPlayerClientResponse(BaseModel):
    user_id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    picture: Optional[str] = None

class GameViewSessionResponse(BaseModel):
    id: Optional[UUID]
    period_type: Optional[PeriodType]  # You can change this to an Enum if needed
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    access_status: AccessStatus  # You can change this to an Enum if needed
    session_status: SessionStatus  # You can change this to an Enum if needed
    view_access: ViewAccess
    players: List[GameViewSessionPlayerClientResponse]

class GameViewManagerResponse(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    picture: Optional[str] = None
    pass


class GameViewGroupResponse(BaseModel):
    id: str
    name: str
    managers: List[GameViewManagerResponse] = []
    pass


class GameViewArenaResponse(BaseModel):
    id: str
    name: str
    group: Optional[GameViewGroupResponse] = None
    sessions: List[GameViewSessionResponse] = []

class GameViewClientResponse(BaseModel):
    id: str
    game_name: Optional[str] = None
    client_name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None
    online_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    game_type: Optional[GameType] = None
    playing_type: Optional[PlayingType] = None
    total_players: Optional[int] = 0
    total_managers: Optional[int] = 0
    total_groups: Optional[int] = 0
    arenas: List[GameViewArenaResponse] = []
    tags: List[str] = []
