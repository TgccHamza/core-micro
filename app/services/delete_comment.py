from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import ProjectComment
import logging

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
    Check if the given user is the owner of the comment.
    """
    if comment.user_id != user_id:
        logger.warning(f"Unauthorized delete attempt by user {user_id} for comment {comment.id}.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this comment.",
        )

def delete_comment(db: Session, comment_id: str, user_id: str) -> dict:
    """
    Delete a comment by ID if the user is the owner.
    """
    # Retrieve the comment
    comment = get_comment_by_id(db, comment_id)

    # Check ownership
    is_comment_owner(comment, user_id)

    # Delete the comment
    db.delete(comment)
    db.commit()

    logger.info(f"Comment with ID {comment_id} deleted by user {user_id}.")
    return {"detail": "Comment successfully deleted."}
