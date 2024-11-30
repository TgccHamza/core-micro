from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GroupUsers, Group, GroupProjects


async def get_manager_email_by_game(game_id: str, session: AsyncSession) -> Sequence[str]:
    result = await session.execute(
        select(GroupUsers.user_email)
        .distinct()  # Ensures unique email addresses
        .join(GroupProjects, GroupUsers.group_id == GroupProjects.group_id)
        .where(GroupProjects.project_id == game_id)
    )
    return result.scalars().all()

