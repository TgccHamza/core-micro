
from pydantic import BaseModel

class FavoriteResponse(BaseModel):
    id: str
    user_id: str
    project_id: str

    class Config:
        orm_mode = True