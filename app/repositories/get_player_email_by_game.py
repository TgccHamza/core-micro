from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSessionPlayers, ArenaSession


async def get_player_email_by_game(game_id: str, session: AsyncSession) -> Sequence[str]:
    result = await session.execute(
        select(ArenaSessionPlayers.user_email)
        .distinct()  # Ensures unique email addresses
        .join(ArenaSession, ArenaSession.id == ArenaSessionPlayers.session_id)
        .where(ArenaSession.project_id == game_id)
    )
    return result.scalars().all()
