from pydantic import BaseModel


class RemoveManagerFromGroupByEmailResponse(BaseModel):
    group_id: str
    manager_email: str
    message: str
