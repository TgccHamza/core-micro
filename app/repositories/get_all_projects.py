from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project


async def get_all_projects(session: AsyncSession) -> Sequence[Project]:
    """
    Asynchronously fetch  projects.

    Args:
        session (AsyncSession): The asynchronous database session.

    Returns:
        List: List of all game responses.
    """
    result = await session.execute(
        select(Project)
        .order_by(Project.created_at.desc())
    )
    return result.scalars().all()  # Fetches the first object
