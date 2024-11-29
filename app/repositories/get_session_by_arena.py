from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSession


async def get_session_by_arena(arena_id: str, session: AsyncSession) -> Sequence[ArenaSession]:
    result = await session.execute(
        select(ArenaSession)
        .where(
            ArenaSession.arena_id == arena_id
        )
    )
    return result.scalars().all()  # Extract ORM objects
