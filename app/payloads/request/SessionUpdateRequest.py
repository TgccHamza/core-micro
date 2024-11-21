from uuid import UUID

from pydantic import BaseModel
from typing import Optional

class SessionUpdateRequest(BaseModel):
    arena_id: UUID
    project_id: Optional[UUID]