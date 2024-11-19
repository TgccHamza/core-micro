from typing import Optional
from pydantic import BaseModel

# Arena creation schema, allowing association with only one group upon creation
class ArenaUpdateRequest(BaseModel):
    name: Optional[str] = None

