from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import ModuleForType
from app.models import ProjectModule


async def get_module_by_game_by_type(game_id: str, types: list[ModuleForType], session: AsyncSession) -> Sequence[
    ProjectModule]:
    """
    Fetches modules of a game by game ID and a list of types.

    Args:
        game_id (str): The ID of the game to fetch modules for.
        types (list[ModuleForType]): A list of types to filter modules by.
        session (AsyncSession): The asynchronous SQLAlchemy session.

    Returns:
        list[ProjectModule]: A list of ProjectModule objects or an empty list if none are found.
    """
    result = await session.execute(
        select(ProjectModule).where(
            ProjectModule.project_id == game_id,
            ProjectModule.type.in_([str(mtype) for mtype in types])  # Correct usage of in_
        )
    )
    return result.scalars().all()
