from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GroupUsers, Group


async def get_manager_by_group(group_id: str, session: AsyncSession) -> Sequence[GroupUsers]:
    result = await session.execute(
        select(GroupUsers)
        .distinct()  # Ensures unique email addresses
        .where(GroupUsers.group_id == group_id)
    )
    return result.scalars().all()
