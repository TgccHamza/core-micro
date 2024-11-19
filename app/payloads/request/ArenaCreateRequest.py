from uuid import UUID

from pydantic import BaseModel
from typing import  Optional, List


# Arena creation schema, allowing association with only one group upon creation
class ArenaCreateRequest(BaseModel):
    name: str
    group_id: UUID  # Only one group is allowed on creation

