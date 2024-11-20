from pydantic import BaseModel
from typing import Optional, List
from app.enums import GameType, PlayingType
from datetime import datetime


class ArenaResponse(BaseModel):
    id: str
    name: str


class ProjectUserResponse(BaseModel):
    user_id: str


class EventGameResponse(BaseModel):
    id: str
    game_name: Optional[str] = None
    client_name: Optional[str] = None
    visibility: Optional[str] = None
    online_date: Optional[datetime] = None
    game_type: Optional[GameType] = None
    playing_type: Optional[PlayingType] = None
    tags: List[str] = []
    total_players: Optional[int] = 0


class ManagerResponse(BaseModel):
    id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    picture: Optional[str] = None
    pass


class GroupResponse(BaseModel):
    id: str
    name: str
    managers: List[ManagerResponse] = []
    arenas: List[ArenaResponse] = []
    pass


class RecentGameResponse(BaseModel):
    id: str
    game_name: Optional[str] = None
    client_name: Optional[str] = None
    visibility: Optional[str] = None
    online_date: Optional[datetime] = None
    game_type: Optional[GameType] = None
    playing_type: Optional[PlayingType] = None
    total_players: Optional[int] = 0
    groups: List[GroupResponse] = []


class FavoriteGameResponse(BaseModel):
    id: str
    game_name: Optional[str] = None
    client_name: Optional[str] = None
    visibility: Optional[str] = None
    online_date: Optional[datetime] = None
    game_type: Optional[GameType] = None
    playing_type: Optional[PlayingType] = None
    total_players: Optional[int] = 0
    groups: List[GroupResponse] = []


class AdminSpaceClientResponse(BaseModel):
    events: List[EventGameResponse] = []
    favorite_games: List[FavoriteGameResponse] = []
    recent_games: List[RecentGameResponse] = []
