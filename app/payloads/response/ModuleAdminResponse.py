from pydantic import BaseModel
from typing import Optional

from app.enums import ModuleType, ModuleForType


class ModuleAdminResponse(BaseModel):
    id: str
    name: Optional[str] = None
    order: Optional[int] = 0
    template_code: Optional[str] = None
    type: Optional[ModuleType] = None
    module_for: Optional[ModuleForType] = None
