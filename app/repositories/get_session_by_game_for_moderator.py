from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSession


async def get_session_by_game_for_moderator(game_id: str, user_email: str, session: AsyncSession) -> Sequence[
    ArenaSession]:
    result = await session.execute(
        select(ArenaSession)
        .where(
            ArenaSession.project_id == game_id,
            ArenaSession.super_game_master_mail == user_email
        )
    )
    return result.scalars().all()  # Extract ORM objects
