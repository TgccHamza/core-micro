from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSession, ArenaSessionPlayers


async def get_players_by_session_db_index_only(db_index: str,
                                               session: AsyncSession) -> Sequence[ArenaSessionPlayers]:
    """
    Fetches a single project (game) by game ID and organization code.

    Args:
        db_index (str): The ID of the session to fetch.
        session (AsyncSession): The asynchronous SQLAlchemy session.

    Returns:
        ArenaSession: A single Project object or None if not found.
    """
    result = await session.execute(
        select(ArenaSessionPlayers)
        .join(ArenaSession, ArenaSession.id == ArenaSessionPlayers.session_id)
        .where(
            ArenaSession.db_index == db_index
        )
    )
    return result.scalars().all()  # Fetches a single object
