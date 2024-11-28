from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import ProjectComment
import logging

from app.payloads.request.ProjectCommentUpdateRequest import ProjectCommentUpdateRequest

logger = logging.getLogger(__name__)

def get_comment_by_id(db: Session, comment_id: str) -> ProjectComment:
    """
    Retrieve a comment by ID.
    """
    comment = db.query(ProjectComment).filter(ProjectComment.id == comment_id).first()
    if not comment:
        logger.error(f"Comment with ID {comment_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    return comment

def is_comment_owner(comment: ProjectComment, user_id: str) -> None:
    """
    Check if the user is the owner of the comment.
    """
    if comment.user_id != user_id:
        logger.warning(f"Unauthorized update attempt by user {user_id} for comment {comment.id}.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to edit this comment.",
        )

def update_comment(
    db: Session, comment_id: str, updated_data: ProjectCommentUpdateRequest, user_id: str
) -> ProjectComment:
    """
    Update an existing comment if the user is the owner.
    """
    # Retrieve the comment
    comment = get_comment_by_id(db, comment_id)

    # Check ownership
    is_comment_owner(comment, user_id)

    # Update comment fields
    if updated_data.comment_text is not None:
        comment.comment_text = updated_data.comment_text

    # Commit changes and refresh
    db.commit()
    db.refresh(comment)

    logger.info(f"Comment with ID {comment_id} updated by user {user_id}.")
    return comment
