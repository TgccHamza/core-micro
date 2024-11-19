from uuid import UUID

from pydantic import BaseModel


# Schema for dissociating an arena from a specific group
class ArenaDisassociationRequest(BaseModel):
    group_id: UUID
