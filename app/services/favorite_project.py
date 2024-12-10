from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.models import ProjectFavorite
from app.repositories.check_user_has_favorite_project import check_user_has_favorite_project

from app.repositories.get_favorite_project import get_favorite_project

logger = logging.getLogger(__name__)

async def favorite_project(
        db: AsyncSession,
        user_id: str,
        project_id: str,
        raise_on_duplicate: bool = False
) -> Optional[ProjectFavorite]:
    """
    Add a project to a user's favorites with enhanced error handling and logging.

    Args:
        db (Session): Database session
        user_id (str): ID of the user favoriting the project
        project_id (str): ID of the project to be favorited
        raise_on_duplicate (bool, optional): Whether to raise an exception on duplicate. Defaults to False.

    Returns:
        Optional[models.ProjectFavorite]: The created favorite project record

    Raises:
        HTTPException: If the project is already favorited and raise_on_duplicate is True
        SQLAlchemyError: For database-related errors
    """
    try:
        # Validate input parameters
        if not user_id or not project_id:
            raise ValueError("User ID and Project ID must be provided")

        # Check if the project is already favorited
        existing_favorite = await get_favorite_project(user_id=user_id, project_id=project_id, session=db)

        # Handle duplicate favorites based on flag
        if existing_favorite:
            if raise_on_duplicate:
                logger.warning(f"Duplicate favorite attempt: User {user_id}, Project {project_id}")
                raise HTTPException(
                    status_code=400,
                    detail="Project is already in favorites"
                )
            return existing_favorite

        # Create a new favorite record
        favorite = ProjectFavorite(
            user_id=user_id,
            project_id=project_id
        )

        # Add and commit in a transactional manner
        db.add(favorite)
        await db.commit()

        # Refresh to get any database-generated attributes
        await db.refresh(favorite)

        # Log successful favorite addition
        logger.info(f"Project {project_id} favorited by user {user_id}")

        return favorite

    except ValueError as ve:
        # Handle invalid input parameters
        logger.error(f"Invalid input: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))

    except SQLAlchemyError as sa_err:
        # Rollback the transaction on database errors
        await db.rollback()
        logger.error(f"Database error when favoriting project: {sa_err}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the favorite"
        )

    except Exception as e:
        # Catch-all for unexpected errors
        await db.rollback()
        logger.error(f"Unexpected error in favorite_project: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )