from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project, GroupProjects


async def get_games_by_group(group_id: str, session: AsyncSession) -> Sequence[Project]:
    """
    Fetches a single project (game) by game ID and organization code.

    Args:
        group_id (str): The ID of the group to fetch.
        org_id (str): The organization code.
        session (AsyncSession): The asynchronous SQLAlchemy session.

    Returns:
        Project: A single Project object or None if not found.
    """
    result = await session.execute(
        select(Project)
        .join(GroupProjects, GroupProjects.project_id == Project.id)
        .where(
            GroupProjects.group_id == group_id
        )
    )
    return result.scalars().all()  # Fetches a single object
