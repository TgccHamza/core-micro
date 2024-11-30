from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project
from app.repositories.get_game_by_id import get_game_by_id


async def get_project(db: AsyncSession, org_id: str, project_id: str):
    """
    Retrieves a project by its organisation code and project ID.

    Args:
        db: The database session instance.
        org_id (str): The organisation code.
        project_id (int): The project ID.

    Returns:
        Project: The project instance if found.

    Raises:
        HTTPException: If the project is not found.
    """
    project = await get_game_by_id(project_id, org_id, db)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} for organisation {org_id} not found."
        )

    return project


async def config_client_game(db: AsyncSession, org_id: str, project_id: str):
    """
    Configures the client game by fetching the associated project.

    Args:
        db: The database session instance.
        org_id (str): The organisation code.
        project_id (int): The project ID.

    Returns:
        Project: The project instance.
    """
    project = await get_project(db, org_id, project_id)

    # Additional logic for configuring the game can go here, such as client-specific settings.

    return project
