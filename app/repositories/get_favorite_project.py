from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import ProjectFavorite


async def get_favorite_project(user_id: str, project_id: str,
                                          session: AsyncSession) -> ProjectFavorite | None:
    result = await session.execute(
        select(ProjectFavorite)
        .distinct()  # Ensures unique email addresses
        .where(ProjectFavorite.project_id == project_id, ProjectFavorite.user_id == user_id)
        .limit(1)
    )
    return result.scalar()
