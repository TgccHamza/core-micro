from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CommentLikesResponse(BaseModel):
    user_id: Optional[str]
    created_at: datetime

class ProjectCommentResponse(BaseModel):
    id: str
    project_id: Optional[str]
    user_id: Optional[str]
    comment_text: Optional[str]
    visible: Optional[bool]
    created_at: datetime
    updated_at: Optional[datetime]
    likes: Optional[list[CommentLikesResponse]] = []

    class Config:
        orm_mode = True