from pydantic import BaseModel


class ProjectCommentUpdateRequest(BaseModel):
    comment_text: str