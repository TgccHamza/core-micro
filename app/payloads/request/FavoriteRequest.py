from pydantic import BaseModel

class FavoriteBase(BaseModel):
    user_id: str
    project_id: str