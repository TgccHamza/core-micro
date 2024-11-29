from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project


async def get_all_projects_by_org(org_id: str, session: AsyncSession) -> Sequence[Project]:
    """
    Asynchronously fetch recent projects for an organization.

    Args:
        session (AsyncSession): The asynchronous database session.
        org_id (str): Organization identifier.

    Returns:
        List: List of all game responses.
    """
    result = await session.execute(
        select(Project)
        .where(Project.organisation_code == org_id)
        .order_by(Project.created_at.desc())
    )
    return result.scalars().all()  # Fetches the first object
