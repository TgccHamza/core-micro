from pydantic import BaseModel
from typing import Optional
from app.enums import ActivationStatus
from datetime import datetime


class ProjectAdminResponse(BaseModel):
    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    db_index: Optional[str] = None
    slug: Optional[str] = None
    visibility: Optional[str] = "public"
    organisation_code: Optional[str] = None
    activation_status: Optional[ActivationStatus] = ActivationStatus.ACTIVE
    client_id: Optional[str] = None
    client_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


