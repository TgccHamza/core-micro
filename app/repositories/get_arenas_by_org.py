from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Arena, GroupArenas


async def get_arenas_by_org(org_id: str, session: AsyncSession) -> Sequence[Arena]:
    """
    Fetches all arenas associated with a specific group ID.
    :param org_id: The ID of the organisation to filter arenas.
    :param session: The async session
    :return: A list of Arena ORM objects.
    """

    result = await session.execute(
        select(Arena).where(
            Arena.organisation_code == org_id
        )
    )

    return result.scalars().all()
