from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import ArenaSessionPlayers


async def get_players_by_session(session_id: str, session: AsyncSession) -> Sequence[ArenaSessionPlayers]:
    result = await session.execute(
        select(ArenaSessionPlayers)
        .where(
            ArenaSessionPlayers.session_id == session_id
        )
    )
    return result.scalars().all()  # Extract ORM objects
