from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Project
from app.repositories.get_game_by_id_only import get_game_by_id_only


async def get_project(db: AsyncSession, project_id: str) -> Project:
    """
    Fetches a project by its ID from the database.

    Args:
        db (Session): The database session instance.
        project_id (str): The ID of the project.

    Returns:
        Project: The project instance if found.

    Raises:
        HTTPException: If the project is not found.
    """
    project = await get_game_by_id_only(project_id, db)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found."
        )

    return project
