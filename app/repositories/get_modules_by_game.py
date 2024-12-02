from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import ModuleForType
from app.models import ProjectModule


async def get_modules_by_game(game_id: str, session: AsyncSession) -> Sequence[ProjectModule]:
    """
    Fetches modules of a game by game ID and a list of types.

    Args:
        game_id (str): The ID of the game to fetch modules for.
        session (AsyncSession): The asynchronous SQLAlchemy session.

    Returns:
        list[ProjectModule]: A list of ProjectModule objects or an empty list if none are found.
    """
    result = await session.execute(
        select(ProjectModule).where(
            ProjectModule.project_id == game_id  # Correct usage of in_
        )
    )
    return result.scalars().all()