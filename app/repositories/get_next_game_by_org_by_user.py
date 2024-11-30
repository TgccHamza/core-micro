from sqlalchemy import select, asc, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models import Project, GroupUsers, ArenaSessionPlayers, ArenaSession, GroupProjects


async def get_next_game_by_org_by_user(org_id: str, user_email: str, session: AsyncSession) -> Project:
    """
    Fetches the next project (game) by organization code, ordered by start_time,
    ensuring that the project ID exists in relevant subqueries.

    Args:
        org_id (str): The organization code.
        user_email (str): The user's email.
        session (AsyncSession): The asynchronous SQLAlchemy session.

    Returns:
        Project: The next Project object or None if not found.
    """
    # Alias for Project to reference in subqueries
    project_alias = aliased(Project)

    # Subquery to check if the user exists in group_projects related to the project
    group_project_exists = exists(
        select(GroupProjects.project_id)
        .join(GroupUsers, GroupProjects.group_id == GroupUsers.group_id)
        .where(
            GroupUsers.user_email == user_email,
            GroupProjects.project_id == project_alias.id  # Ensures project is part of group_projects
        )
    )

    # Subquery to check if the user exists in arena session players related to the project
    arena_project_exists = exists(
        select(ArenaSession.project_id)
        .join(ArenaSessionPlayers, ArenaSession.id == ArenaSessionPlayers.session_id)
        .where(
            ArenaSessionPlayers.user_email == user_email,
            ArenaSession.project_id == project_alias.id  # Ensures project is part of arena sessions
        )
    )

    # Main query to fetch the next project by organization code
    result = await session.execute(
        select(Project)
        .where(
            Project.organisation_code == org_id,
            group_project_exists | arena_project_exists  # Combines the `exists` filters
        )
        .order_by(asc(Project.start_time))  # Orders by start time
    )

    return result.scalars().first()  # Fetches the first matching project
