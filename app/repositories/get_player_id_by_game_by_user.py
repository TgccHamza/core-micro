from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSessionPlayers, ArenaSession


async def get_player_id_by_game_by_user(game_id: str, user_id: str,
                                        session: AsyncSession) -> ArenaSessionPlayers | None:
    result = await session.execute(
        select(ArenaSessionPlayers)
        .distinct()  # Ensures unique email addresses
        .join(ArenaSession, ArenaSession.id == ArenaSessionPlayers.session_id)
        .where(ArenaSession.project_id == game_id,
               ArenaSessionPlayers.user_id == user_id)
    )
    return result.scalar()
