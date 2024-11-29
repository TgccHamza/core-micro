from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSessionPlayers, ArenaSession


async def count_session_players(db: AsyncSession, module_game_id: str, game_id: str) -> int:
    """
    Asynchronous player count query.

    Args:
        db (AsyncSession): The asynchronous database session.
        module_game_id (str): The module game ID.
        game_id (str): The  game ID.

    Returns:
        int: Total number of players.
    """
    result = await db.execute(
        select(func.count())
        .select_from(
            ArenaSessionPlayers
        )
        .join(
            ArenaSession, ArenaSession.id == ArenaSessionPlayers.session_id
        )
        .where(ArenaSession.player_module_id == module_game_id, ArenaSession.project_id == game_id)
    )
    return result.scalar()  # Fetches the count as an integer
