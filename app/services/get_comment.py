from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import ProjectComment
import logging

from app.payloads.response.ProjectCommentResponse import ProjectCommentResponse

logger = logging.getLogger(__name__)


def get_comment(db: Session, comment_id: str) -> ProjectCommentResponse:
    """
    Retrieve a single comment by ID.
    :param db: SQLAlchemy database session
    :param comment_id: ID of the comment to retrieve
    :return: ProjectCommentResponse schema object
    """
    try:
        # Fetch the comment
        comment = db.query(ProjectComment).filter(ProjectComment.id == comment_id).first()

        if not comment:
            logger.warning(f"Comment with ID {comment_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )

        logger.info(f"Comment with ID {comment_id} retrieved successfully.")
        # Convert to schema response
        return ProjectCommentResponse.from_orm(comment)

    except Exception as e:
        logger.error(f"Error retrieving comment with ID {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the comment"
        )
