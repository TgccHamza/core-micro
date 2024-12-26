from pydantic import BaseModel


class AssignManagerToGroupByEmailResponse(BaseModel):
    message: str = "Manager assigned to group successfully"
    group_id: str
    manager_email: str

    class Config:
        orm_mode = True