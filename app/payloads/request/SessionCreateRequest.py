from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from typing import Optional

class SessionCreateRequest(BaseModel):
    arena_id: UUID
    game_id: Optional[UUID]