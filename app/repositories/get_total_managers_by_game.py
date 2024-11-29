from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Group, GroupUsers, GroupProjects


async def get_total_managers_by_game(game_id: str, session: AsyncSession) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(GroupUsers)
        .join(Group, Group.id == GroupUsers.group_id)
        .join(GroupProjects, Group.id == GroupProjects.group_id)
        .distinct(GroupUsers.user_id)
        .where(
            GroupProjects.project_id == game_id
        )
    )
    return result.scalar()
