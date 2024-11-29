from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GroupProjects


async def get_total_groups_by_game(game_id: str, session: AsyncSession) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(GroupProjects)
        .distinct(GroupProjects.group_id)
        .where(
            GroupProjects.project_id == game_id
        )
    )
    return result.scalar()
