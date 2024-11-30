from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project


async def get_recent_projects_by_org_by_user(org_id: str, user_email: str, session: AsyncSession) -> Sequence[Project]:
    """
    Asynchronously fetch recent projects for an organization.

    Args:
        session (AsyncSession): The asynchronous database session.
        org_id (str): Organization identifier.

    Returns:
        List: List of recent game responses.
    """
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
        .limi(5)
    )

    return result.scalars().all()  # Fetches the first matching project
