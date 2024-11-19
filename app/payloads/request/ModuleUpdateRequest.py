from pydantic import BaseModel
from typing import  Optional

class ModuleUpdateRequest(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    order: Optional[int] = 0