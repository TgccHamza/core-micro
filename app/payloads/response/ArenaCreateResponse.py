
from pydantic import BaseModel

class ArenaCreateResponse(BaseModel):
    id: str
    name: str

