from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project


async def get_next_game_by_org(org_id: str, session: AsyncSession) -> Project:
    """
    Fetches the next project (game) by organization code, ordered by start_time.

    Args:
        org_id (str): The organization code.
        session (AsyncSession): The asynchronous SQLAlchemy session.

    Returns:
        Project: The next Project object or None if not found.
    """
    result = await session.execute(
        select(Project)
        .where(Project.organisation_code == org_id)
        .order_by(asc(Project.start_time))
    )
    return result.scalars().first()  # Fetches the first object
