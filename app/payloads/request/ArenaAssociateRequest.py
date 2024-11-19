from uuid import UUID

from pydantic import BaseModel


class ArenaAssociateRequest(BaseModel):
    group_id: UUID