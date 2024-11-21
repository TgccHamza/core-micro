from pydantic import BaseModel


class ProjectCommentCreateRequest(BaseModel):
    comment_text: str