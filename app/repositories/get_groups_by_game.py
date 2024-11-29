from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Group, GroupProjects


async def get_groups_by_game(game_id: str, session: AsyncSession) -> Sequence[Group]:
    """
    Fetches all groups associated with a specific game ID.
    :param game_id: The ID of the game to filter groups by.
    :param session: The async session
    :return: A list of Group ORM objects.
    """

    result = await session.execute(
        select(Group).join(
            GroupProjects, GroupProjects.group_id == Group.id
        ).where(
            GroupProjects.project_id == game_id
        )
    )
    return result.scalars().all()
