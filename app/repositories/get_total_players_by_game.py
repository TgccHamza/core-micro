from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSessionPlayers, ArenaSession


async def get_total_players_by_game(game_id: str, session: AsyncSession) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(ArenaSessionPlayers)
        .join(ArenaSession, ArenaSession.id == ArenaSessionPlayers.session_id)
        .distinct(ArenaSessionPlayers.user_id)
        .where(
            ArenaSession.project_id == game_id
        )
    )
    return result.scalar()
