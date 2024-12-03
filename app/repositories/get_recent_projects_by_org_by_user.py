from typing import Sequence

from sqlalchemy import select, asc, exists, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models import Project, ArenaSessionPlayers, ArenaSession, GroupProjects, GroupUsers


async def get_recent_projects_by_org_by_user(org_id: str, user_id: str, session: AsyncSession) -> Sequence[Project]:
    """
    Asynchronously fetch recent projects for an organization.

    Args:
        session (AsyncSession): The asynchronous database session.
        org_id (str): Organization identifier.
        user_id (str): user identifier.

    Returns:
        List: List of recent game responses.
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
            group_project_exists | player_session_project_exists | session_project_exists  # Combines the `exists` filters
        )
        .order_by(asc(Project.start_time))  # Orders by start time
        .limit(5)
    )

    # Main query to fetch the next project by organization code
    result = await session.execute(query)

    return result.scalars().all()  # Fetches the first matching project
