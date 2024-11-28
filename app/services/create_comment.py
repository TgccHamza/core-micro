from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import ProjectComment
import logging
from app.payloads.response.ProjectCommentResponse import ProjectCommentResponse

logger = logging.getLogger(__name__)


def create_comment(
        db: Session,
        project_id: str,
        user_id: str,
        comment_text: str
) -> ProjectCommentResponse:
    """
    Create a new project comment.
    :param comment_text: the comment text
    :param user_id: User commented
    :param project_id: the game
    :param db: SQLAlchemy database session
    :return: ProjectCommentResponse schema object
    """
    try:
        # Construct the new comment object
        new_comment = ProjectComment(
            project_id=project_id,
            user_id=user_id,
            comment_text=comment_text,
            visible=True  # Defaults to visible; modify as per your business rules
        )

        # Persist the new comment
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)

        logger.info(
            f"Comment created with ID {new_comment.id} for project {project_id} by user {user_id}.")

        # Convert to response schema
        return ProjectCommentResponse.from_orm(new_comment)

    except Exception as e:
        logger.error(f"Error creating comment for project {project_id} by user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the comment"
        )
