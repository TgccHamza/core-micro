from pydantic import BaseModel
from typing import Optional

class DeleteGroupResponse(BaseModel):
    message: Optional[str] = None
    group_id: Optional[str] = None
