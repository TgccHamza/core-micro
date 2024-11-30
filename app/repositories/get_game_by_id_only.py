from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project


async def get_game_by_id_only(game_id: str,  session: AsyncSession) -> Project:
    """
    Fetches a single project (game) by game ID and organization code.

    Args:
        game_id (str): The ID of the game to fetch.
        session (AsyncSession): The asynchronous SQLAlchemy session.

    Returns:
        Project: A single Project object or None if not found.
    """
    result = await session.execute(
        select(Project).where(
            Project.id == game_id
        )
    )
    return result.scalar()  # Fetches a single object
