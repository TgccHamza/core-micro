from pydantic import BaseModel
from typing import Optional, Any

class InviteManagerResponse(BaseModel):
    message: str