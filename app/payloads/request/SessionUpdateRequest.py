from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from typing import Optional, List

from app.enums import PeriodType, AccessStatus, SessionStatus, ViewAccess

class SessionUpdateRequest(BaseModel):
    arena_id: UUID
    project_id: Optional[UUID]
    period_type: PeriodType  # You can change this to an Enum if needed
    start_time: datetime
    end_time: Optional[datetime]
    access_status: AccessStatus  # You can change this to an Enum if needed
    session_status: SessionStatus  # You can change this to an Enum if needed
    view_access: ViewAccess  # You can change this to an Enum if needed
    user_ids: List[UUID]