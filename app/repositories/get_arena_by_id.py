from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Arena


async def get_arena_by_id(arena_id: str, session: AsyncSession) -> Arena:
    """
    Fetches all arenas associated with a specific group ID.
    :param arena_id: The ID of the group to filter arenas.
    :param session: The async session
    :return: A list of Arena ORM objects.
    """

    result = await session.execute(
        select(Arena).where(
            Arena.id == arena_id
        )
    )
    return result.scalar()
