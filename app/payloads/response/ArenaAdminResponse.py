from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from app.enums import PeriodType, AccessStatus, ViewAccess, SessionStatus


class GameResponse(BaseModel):
    id: str
    name: str
    type: str
    project_id: str
    order: Optional[int] = 0

class SessionPlayerClientResponse(BaseModel):
    user_id: str
    game: GameResponse

class ArenaSessionResponse(BaseModel):
    id: str
    game: GameResponse
    period_type: PeriodType
    start_time: datetime
    end_time: datetime
    access_status: AccessStatus
    session_status: SessionStatus
    view_access: ViewAccess
    players: List[SessionPlayerClientResponse]


class ArenaAdminResponse(BaseModel):
    id: str
    name: str
    sessions: List[ArenaSessionResponse]
