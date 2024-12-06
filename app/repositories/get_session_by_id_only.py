from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSession


async def get_session_by_id_only(session_id: str, session: AsyncSession) -> ArenaSession:
    """
    Fetches a single project (game) by game ID and organization code.

    Args:
        session_id (str): The ID of the session to fetch.
        session (AsyncSession): The asynchronous SQLAlchemy session.

    Returns:
        ArenaSession: A single Project object or None if not found.
    """
    result = await session.execute(
        select(ArenaSession).where(
            ArenaSession.id == session_id
        )
    )
    return result.scalar()  # Fetches a single object
