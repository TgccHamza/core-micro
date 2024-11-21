from pydantic import BaseModel
from typing import Optional


class InvitePlayerResponse(BaseModel):
    message: str