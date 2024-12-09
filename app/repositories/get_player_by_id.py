from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSessionPlayers


async def get_player_by_id(player_id: str, org_id: str, session: AsyncSession) -> ArenaSessionPlayers | None:
    result = await session.execute(
        select(ArenaSessionPlayers)
        .where(
            ArenaSessionPlayers.id == player_id,
            ArenaSessionPlayers.organisation_code == org_id
        )
        .limit(1)
    )
    return result.scalar()  # Extract ORM objects
