from pydantic import BaseModel


class AssignGameToGroupResponse(BaseModel):
    group_id: str
    game_id: str
    message: str
