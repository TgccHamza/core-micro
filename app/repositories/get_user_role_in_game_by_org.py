from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project, GroupUsers, ArenaSessionPlayers, ArenaSession, GroupProjects


async def get_user_role_in_game_by_org(
        org_id: str, user_email: str, game_id: str, session: AsyncSession
) -> str | None:
    """
    Determines the role of a user in a game within an organization.

    Args:
        org_id (str): The organization code.
        user_email (str): The user's email.
        game_id (str): The game ID.
        session (AsyncSession): The asynchronous SQLAlchemy session.

    Returns:
        str: The role of the user ('manager', 'moderator', 'player', or None).
    """

    manager_query = (
        select(GroupProjects.project_id)
        .join(GroupUsers, GroupProjects.group_id == GroupUsers.group_id)
        .where(
            GroupUsers.user_email == user_email,
            GroupProjects.project_id == game_id,
        )
    )

    # Manager role
    result = await session.execute(manager_query)
    if result.scalar() is not None:
        return "manager"


    player_query = (
        select(ArenaSessionPlayers.session_id)
        .join(ArenaSession, ArenaSessionPlayers.session_id == ArenaSession.id)
        .where(
            ArenaSessionPlayers.user_email == user_email,
            ArenaSession.project_id == game_id,
            ArenaSession.organisation_code == org_id,
        )
    )

    # Player role
    result = await session.execute(player_query)
    if result.scalar() is not None:
        return "player"


    moderator_query = (
        select(ArenaSession.project_id)
        .where(
            ArenaSession.super_game_master_mail == user_email,
            ArenaSession.project_id == game_id,
            ArenaSession.organisation_code == org_id,
        )
    )

    # Moderator role
    result = await session.execute(moderator_query)
    if result.scalar() is not None:
        return "moderator"


    # No access
    return None
