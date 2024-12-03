from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSessionPlayers


async def get_player_id_by_session(session_id: str, session: AsyncSession) -> Sequence[str]:
    result = await session.execute(
        select(ArenaSessionPlayers.user_id)
        .distinct()  # Ensures unique email addresses
        .where(ArenaSessionPlayers.session_id == session_id)
    )
    return result.scalars().all()
