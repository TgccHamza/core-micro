from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GroupArenas, Group


async def get_group_by_id(group_id: str, session: AsyncSession) -> Group:
    """
    Fetches all arenas associated with a specific group ID.
    :param group_id: The ID of the group.
    :param session: The async session
    :return: A list of Arena ORM objects.
    """

    result = await session.execute(
        select(Group).where(
            Group.id == group_id
        )
        .limit(1)
    )
    return result.scalar()