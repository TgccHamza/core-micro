from pydantic import BaseModel


class GroupUpdateRequest(BaseModel):
    name: str
