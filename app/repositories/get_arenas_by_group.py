from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Arena, GroupArenas


async def get_arenas_by_group(group_id: str, session: AsyncSession) -> Sequence[Arena]:
    """
    Fetches all arenas associated with a specific group ID.
    :param group_id: The ID of the group to filter arenas.
    :param session: The async session
    :return: A list of Arena ORM objects.
    """

    result = await session.execute(
        select(Arena).join(
            GroupArenas, GroupArenas.arena_id == Arena.id
        ).where(
            GroupArenas.group_id == group_id
        )
    )
    return result.scalars().all()
