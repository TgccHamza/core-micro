from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Group


async def get_groups_by_org(org_id: str, session: AsyncSession) -> Sequence[Group]:
    """
    Fetches all arenas associated with a specific group ID.
    :param org_id: The ID of the group.
    :param session: The async session
    :return: A list of Arena ORM objects.
    """

    result = await session.execute(
        select(Group).where(
            Group.organisation_code == org_id
        )
    )
    return result.scalars().all()