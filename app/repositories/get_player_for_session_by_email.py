from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSessionPlayers


async def get_player_for_session_by_email(session_id: str, user_email: str, session: AsyncSession) -> ArenaSessionPlayers | None:
    result = await session.execute(
        select(ArenaSessionPlayers)
        .where(
            ArenaSessionPlayers.session_id == session_id,
            ArenaSessionPlayers.user_email == user_email
        )
        .limit(1)
    )
    return result.scalar() # Extract ORM objects
