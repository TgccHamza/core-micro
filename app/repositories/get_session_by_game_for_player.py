from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSession, ArenaSessionPlayers


async def get_session_by_game_for_player(game_id: str, user_email: str, session: AsyncSession) -> Sequence[
    ArenaSession]:
    result = await session.execute(
        select(ArenaSession)
        .join(ArenaSessionPlayers, ArenaSessionPlayers.session_id == ArenaSession.id)
        .where(
            ArenaSession.project_id == game_id,
            ArenaSessionPlayers.user_email == user_email
        )
    )
    return result.scalars().all()  # Extract ORM objects
