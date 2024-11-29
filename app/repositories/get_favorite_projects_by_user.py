from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project, ProjectFavorite


async def get_favorite_projects_by_user(user_id: str, session: AsyncSession) -> Sequence[Project]:
    """
    Fetches the favorite project (game) by user code

    Args:
        user_id (str): The user code.
        session (AsyncSession): The asynchronous SQLAlchemy session.

    Returns:
        Project: The next Project object or None if not found.
    """
    result = await session.execute(
        select(Project)
        .join(ProjectFavorite, ProjectFavorite.project_id == Project.id)
        .where(ProjectFavorite.user_id == user_id)
    )
    return result.scalars().all()  # Fetches the first object
