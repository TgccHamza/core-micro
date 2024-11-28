from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from app.models import ProjectFavorite


def unfavorite_project(
        db: Session,
        user_id: str,
        project_id: str
) -> Dict[str, str]:
    """
    Remove a project from a user's favorites with comprehensive error handling.

    Args:
        db (Session): Database session
        user_id (str): Identifier of the user
        project_id (str): Identifier of the project to unfavorite

    Returns:
        Dict[str, str]: Confirmation message

    Raises:
        HTTPException: 404 if favorite not found
        HTTPException: 500 for database-related errors
    """
    try:
        # Attempt to find and delete the favorite in a single query
        rows_affected = db.query(ProjectFavorite) \
            .filter_by(user_id=user_id, project_id=project_id) \
            .delete(synchronize_session=False)

        # Check if any rows were actually deleted
        if rows_affected == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No favorite found for user {user_id} and project {project_id}"
            )

        # Commit the transaction
        db.commit()

        return {"message": "Project successfully removed from favorites"}

    except SQLAlchemyError as e:
        # Rollback the transaction in case of any database error
        db.rollback()

        # Log the error (in a real-world scenario, use proper logging)
        print(f"Database error during unfavorite: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request"
        )
    except Exception as e:
        # Catch any unexpected errors
        db.rollback()

        # Log the unexpected error
        print(f"Unexpected error during unfavorite: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )