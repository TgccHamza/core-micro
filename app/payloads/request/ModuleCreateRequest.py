from pydantic import BaseModel
from typing import  Optional


class ModuleCreateRequest(BaseModel):
    name: str
    type: str
    project_id: str
    order: Optional[int] = 0