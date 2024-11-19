from pydantic import BaseModel
from typing import  Optional

class ModuleAdminResponse(BaseModel):
    id: str
    name: Optional[str] = None
    type: Optional[str] = None
    order: Optional[int] = 0
    template_code: Optional[str] = None
