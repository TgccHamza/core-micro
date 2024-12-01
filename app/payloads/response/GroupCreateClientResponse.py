from datetime import datetime

from pydantic import BaseModel
from typing import  List, Optional
from uuid import UUID

from app.enums import ActivationStatus



class GroupCreateClientResponse(BaseModel):
    id: UUID
    name: str