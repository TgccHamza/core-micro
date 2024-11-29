from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSession


async def get_sessions_by_org(org_id: str, session: AsyncSession) -> Sequence[ArenaSession]:
    result = await session.execute(
        select(ArenaSession)
        .where(
            ArenaSession.organisation_code == org_id
        )
    )
    return result.scalars().all()  # Extract ORM objects
