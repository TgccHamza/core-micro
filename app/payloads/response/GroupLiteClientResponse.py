from pydantic import BaseModel
from uuid import UUID

class GroupLiteClientResponse(BaseModel):
    id: str
    name: str
