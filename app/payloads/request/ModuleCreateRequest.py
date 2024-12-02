from pydantic import BaseModel
from typing import Optional

from app.enums import ModuleType, ModuleForType


class ModuleCreateRequest(BaseModel):
    name: str
    type: str
    project_id: str
    type: ModuleType
    module_for: ModuleForType
    order: Optional[int] = 0
