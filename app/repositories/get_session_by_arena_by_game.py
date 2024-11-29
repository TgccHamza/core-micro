from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSession


async def get_session_by_arena_by_game(game_id: str, db_arena_id: str, session: AsyncSession) -> Sequence[ArenaSession]:
    result = await session.execute(
        select(ArenaSession)
        .where(
            ArenaSession.project_id == game_id,
            ArenaSession.arena_id == db_arena_id
        )
    )
    return result.scalars().all()  # Extract ORM objects
