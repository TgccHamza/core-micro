from pydantic import BaseModel


class RemoveGameFromGroupResponse(BaseModel):
    group_id: str
    game_id: str
    message: str