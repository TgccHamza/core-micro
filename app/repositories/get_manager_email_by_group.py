from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GroupUsers, Group


async def get_manager_email_by_group(group_id: str, session: AsyncSession) -> Sequence[str]:
    result = await session.execute(
        select(GroupUsers.user_email)
        .distinct()  # Ensures unique email addresses
        .join(Group, Group.id == GroupUsers.group_id)
        .where(Group.id == group_id)
    )
    return result.scalars().all()

