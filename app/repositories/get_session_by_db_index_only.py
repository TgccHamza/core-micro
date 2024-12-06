from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSession


async def get_session_by_db_index_only(db_index: str, session: AsyncSession) -> ArenaSession | None:
    """
    Fetches a single project (game) by game ID and organization code.

    Args:
        db_index (str): The ID of the session to fetch.
        session (AsyncSession): The asynchronous SQLAlchemy session.

    Returns:
        ArenaSession: A single Project object or None if not found.
    """

    result = await session.execute(
        select(ArenaSession)
        .where(
            ArenaSession.db_index == db_index
        ).limit(1)
    )
    return result.scalar()
