from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSession, ArenaSessionPlayers


async def get_player_by_session_by_id_only(db_index: str, player_id: str,
                                           session: AsyncSession) -> ArenaSessionPlayers | None:
    """
    Fetches a single project (game) by game ID and organization code.

    Args:
        db_index (str): The ID of the session to fetch.
        player_id (str): The ID of the session to fetch.
        session (AsyncSession): The asynchronous SQLAlchemy session.

    Returns:
        ArenaSession: A single Project object or None if not found.
    """
    result = await session.execute(
        select(ArenaSessionPlayers)
        .join(ArenaSession, ArenaSession.id == ArenaSessionPlayers.session_id)
        .where(
            ArenaSession.db_index == db_index,
            ArenaSessionPlayers.user_id == player_id
        )
    )
    return result.scalar()  # Fetches a single object
