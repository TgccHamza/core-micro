import logging
from typing import Dict, Any
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Project

logger = logging.getLogger(__name__)


def create_project(
        db: Session,
        project_data: Dict[str, Any],
        unique_fields: list[str] = None
) -> Project:
    """
    Create a new project with enhanced error handling and logging.

    Args:
        db (Session): Database session
        project_data (Dict[str, Any]): Dictionary containing project creation details
        unique_fields (list, optional): List of fields to check for uniqueness

    Returns:
        models.Project: Created project instance

    Raises:
        HTTPException: If project creation fails due to integrity or validation errors
    """
    # Validate input data (you might want to add more comprehensive validation)
    if not project_data:
        raise ValueError("Project data cannot be empty")

    # Prepare project creation with explicit field mapping
    project_fields = {
        'name': project_data.get('name'),
        'description': project_data.get('description'),
        'db_index': project_data.get('db_index'),
        'slug': project_data.get('slug'),
        'visibility': project_data.get('visibility'),
        'game_type': project_data.get('game_type'),
        'playing_type': project_data.get('playing_type'),
        'activation_status': project_data.get('activation_status'),
        'organisation_code': project_data.get('organisation_code'),
        'client_id': project_data.get('client_id'),
        'client_name': project_data.get('client_name'),
        'start_time': project_data.get('start_time'),
        'end_time': project_data.get('end_time'),
        'tags': project_data.get('tags')
    }

    # Remove None values to avoid setting optional fields to None
    project_fields = {k: v for k, v in project_fields.items() if v is not None}

    # Create project instance
    db_project = Project(**project_fields)

    try:
        # Add and commit the project
        db.add(db_project)
        db.commit()

        # Refresh to get any database-generated fields
        db.refresh(db_project)

        logger.info(f"Project created successfully: {db_project.slug}")
        return db_project

    except IntegrityError as ie:
        # Rollback the transaction
        db.rollback()

        # Log the specific integrity error
        logger.error(f"Integrity error creating project: {ie}")

        # More informative error message
        raise HTTPException(
            status_code=400,
            detail="Project creation failed. Ensure all unique constraints are met."
        )

    except SQLAlchemyError as e:
        # Catch any other database-related errors
        db.rollback()

        logger.error(f"Database error creating project: {e}")

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while creating the project"
        )

    except Exception as e:
        # Catch any other unexpected errors
        db.rollback()

        logger.error(f"Unexpected error creating project: {e}")

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )
