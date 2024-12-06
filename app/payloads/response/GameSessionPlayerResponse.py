from typing import Optional

from pydantic import BaseModel


class GameSessionPlayerResponse(BaseModel):
    user_id: str
    role: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    picture: Optional[str] = None
    is_game_master: Optional[bool] = False
    is_moderator: Optional[bool] = False
    is_player: Optional[bool] = False
