from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import logging
logger = logging.getLogger(__name__)
from app.models import Project, ProjectFavorite


def list_favorites(
        db: Session,
        user_id: str
) -> List[Project]:
    """
    Retrieve favorite projects for a user with enhanced error handling.

    Args:
        db (Session): Database session
        user_id (str): Unique identifier for the user

    Returns:
        List[models.Project]: List of favorite projects

    Raises:
        ValueError: If user_id is invalid
        SQLAlchemyError: For database-related errors
    """
    # Validate input
    if not user_id:
        logger.error(f"Invalid user_id provided: {user_id}")
        raise ValueError("User ID cannot be empty or None")

    try:
        # Construct query with potential for additional filtering
        query = (
            db.query(Project)
            .join(ProjectFavorite, ProjectFavorite.project_id == Project.id)
            .filter(ProjectFavorite.user_id == user_id)
        )

        # Execute query with performance optimization
        favorites = query.all()

        # Log query results for observability
        logger.info(f"Retrieved {len(favorites)} favorite projects for user {user_id}")

        return favorites

    except SQLAlchemyError as e:
        # Comprehensive error logging
        logger.error(f"Database error retrieving favorites for user {user_id}: {str(e)}")
        raise

    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error in list_favorites: {str(e)}")
        raise
