from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSessionPlayers


async def check_existing_player_by_email_by_session(user_id: str, session_id: str,
                                                    session: AsyncSession) -> str | None:
    result = await session.execute(
        select(ArenaSessionPlayers.user_email)
        .distinct()  # Ensures unique email addresses
        .where(ArenaSessionPlayers.session_id == session_id, ArenaSessionPlayers.user_id == user_id)
        .limit(1)
    )
    return result.scalar()
