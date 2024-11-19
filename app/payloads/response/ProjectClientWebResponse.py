from pydantic import BaseModel
from typing import Optional
from app.enums import ActivationStatus
from datetime import datetime



class ProjectUserResponse(BaseModel):
    user_id: str


class ProjectClientWebResponse(BaseModel):
    id: str
    game_name: Optional[str] = None
    client_id: Optional[str] = None
    online_date: Optional[datetime] = None
    game_end_date: Optional[datetime] = None
    activation_status: Optional[ActivationStatus] = None
    game_users: Optional[ProjectUserResponse] = []


