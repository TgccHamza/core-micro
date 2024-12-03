from sqlalchemy import select, asc, exists, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models import Project, GroupUsers, ArenaSessionPlayers, ArenaSession, GroupProjects


async def get_next_game_by_org_by_user(org_id: str, user_id: str, session: AsyncSession) -> Project:
    """
    Fetches the next project (game) by organization code, ordered by start_time,
    ensuring that the project ID exists in relevant subqueries.

    Args:
        org_id (str): The organization code.
        user_id (str): The user's email.
        session (AsyncSession): The asynchronous SQLAlchemy session.

    Returns:
        Project: The next Project object or None if not found.
    """

    # Subquery to check if the user exists in group_projects related to the project
    group_project_exists = exists(
        select(GroupProjects.project_id)
        .distinct()
        .join(GroupUsers, GroupProjects.group_id == GroupUsers.group_id)
        .where(
            GroupUsers.user_id == user_id,
            GroupProjects.project_id == Project.id  # Ensures project is part of group_projects
        )
    )

    # Subquery to check if the user exists in arena session players related to the project
    player_session_project_exists = exists(
        select(ArenaSession.project_id)
        .distinct()
        .join(ArenaSessionPlayers, ArenaSession.id == ArenaSessionPlayers.session_id)
        .where(
            ArenaSessionPlayers.user_id == user_id
            ,
            ArenaSession.project_id == Project.id  # Ensures project is part of arena sessions
        )
    )

    session_project_exists = exists(
        select(ArenaSession.project_id)
        .distinct()
        .where(
            ArenaSession.super_game_master_id == user_id
            ,
            ArenaSession.project_id == Project.id  # Ensures project is part of arena sessions
        )
    )

    query = (
        select(Project)
        .where(
            Project.organisation_code == org_id,
            group_project_exists | player_session_project_exists | session_project_exists # Combines the `exists` filters
        )
        .order_by(asc(Project.start_time))  # Orders by start time
        .limit(1)
    )

    # Main query to fetch the next project by organization code
    result = await session.execute(query)

    return result.scalar() # Fetches the first matching project
