from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GroupArenas, Group


async def get_groups_by_arena(arena_id: str, session: AsyncSession) -> Sequence[Group]:
    """
    Fetches all arenas associated with a specific group ID.
    :param arena_id: The ID of the group to filter arenas.
    :param session: The async session
    :return: A list of Arena ORM objects.
    """

    result = await session.execute(
        select(Group).join(
            GroupArenas, GroupArenas.group_id == Group.id
        ).where(
            GroupArenas.arena_id == arena_id
        )
    )
    return result.scalars().all()
