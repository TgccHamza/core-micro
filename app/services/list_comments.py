from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models import ProjectComment
import logging

from app.payloads.response.ProjectCommentResponse import ProjectCommentResponse

logger = logging.getLogger(__name__)


def list_comments(
        db: Session,
        project_id: Optional[str] = None,
        visible: bool = True
) -> List[ProjectCommentResponse]:
    """
    List comments based on filters.
    :param db: SQLAlchemy database session
    :param project_id: Optional project ID to filter comments by project
    :param visible: Filter comments by visibility (default: True)
    :return: List of ProjectCommentResponse
    """
    # Build the query dynamically
    filters = [ProjectComment.visible == visible]

    if project_id:
        filters.append(ProjectComment.project_id == project_id)

    try:
        query = db.query(ProjectComment).filter(and_(*filters))
        comments = query.all()
        logger.info(f"Retrieved {len(comments)} comments for project_id={project_id}.")
        return [ProjectCommentResponse.from_orm(comment) for comment in comments]

    except Exception as e:
        logger.error(f"Error retrieving comments: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving comments."
        )
