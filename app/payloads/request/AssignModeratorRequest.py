from pydantic import BaseModel

class AssignModeratorRequest(BaseModel):
    email: str