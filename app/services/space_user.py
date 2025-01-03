from typing import List
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.count_session_players import count_session_players
from app.repositories.get_arenas_by_group import get_arenas_by_group
from app.repositories.get_favorite_projects_by_user import get_favorite_projects_by_user
from app.repositories.get_groups_by_game import get_groups_by_game
from app.repositories.get_manager_by_group import get_manager_by_group
from app.repositories.get_manager_id_by_game import get_manager_id_by_game
from app.repositories.get_next_game_by_org_by_user import get_next_game_by_org_by_user
from app.repositories.get_player_id_by_game_by_user import get_player_id_by_game_by_user
from app.repositories.get_recent_projects_by_org_by_user import get_recent_projects_by_org_by_user
from app.repositories.get_user_role_in_game_by_org import get_user_role_in_game_by_org

logger = logging.getLogger(__name__)
from app.models import Group, Project
from app.payloads.response.EspaceAdminClientResponse import ArenaResponse, ManagerResponse, GroupResponse, \
    RecentGameResponse, FavoriteGameResponse, EventGameResponse, AdminSpaceClientResponse
from app.payloads.response.UserResponse import UserResponse
from app.services.user_service import get_user_service


async def _process_group_managers(
        db_group: Group, users: dict[str, UserResponse], db: AsyncSession
) -> List[ManagerResponse]:
    """
    Process group managers with concurrent user details fetching.

    Args:
        db_group (Group): Group
        users: the users of api salah

    Returns:
        List[GameViewManagerResponse]: Processed manager details
    """
    processed_managers = []

    for manager in (await get_manager_by_group(db_group.id, db)):
        user_detail = users.get(manager.user_id, None)
        processed_manager = ManagerResponse(
            user_id=user_detail.get('user_id') if user_detail else str(manager.user_id),
            email=user_detail.get('user_email') if user_detail else manager.user_email,
            first_name=user_detail.get('first_name') if user_detail else None,
            last_name=user_detail.get('last_name') if user_detail else None,
            picture=user_detail.get('picture') if user_detail else None
        )

        processed_managers.append(processed_manager)

    return processed_managers


async def _process_single_event(db: AsyncSession, project: Project, role: str):
    """
    Process a single project event with player count.

    :param db: Database session
    :param project: Project model instance
    :return: Processed event response
    """
    total_players = await count_session_players(db, project.module_game_id, project.id)

    return EventGameResponse(
        id=project.id,
        game_name=project.name,
        role=role,
        client_name=project.client_name,
        visibility=project.visibility,
        online_date=project.start_time,
        game_type=project.game_type,
        playing_type=project.playing_type,
        total_players=total_players,
        tags=[x.strip() for x in project.tags.split(",")]
    )


async def fetch_favorite_projects(db: AsyncSession, user_id: str):
    """
    Fetch and process favorite projects for a user.

    :param db: Database session
    :param user_id: User identifier
    :return: List of favorite game responses
    """
    favorite_projects = await get_favorite_projects_by_user(user_id, db)
    favorite_tasks = [
        await _process_favorite_project(db, fav_project, user_id)
        for fav_project in favorite_projects
    ]

    return favorite_tasks


async def _process_favorite_project(db: AsyncSession, project, user_id: str):
    """
     Process a single favorite project with details.

    :param db: Database session
    :param project: Favorite project model instance
    :return: Favorite game response
    """

    total_players = await count_session_players(db, project.module_game_id, project.id)
    ids = await get_manager_id_by_game(project.id, db)

    if len(ids) != 0:
        users = await get_user_service().get_users_by_id(list(ids))
    else:
        users = dict()

    role = await get_user_role_in_game_by_org(project.organisation_code, user_id, project.id, db)
    if role == "player":
        player = await get_player_id_by_game_by_user(project.id, user_id, db)
        if player is not None and player.is_game_master:
            role = "game_master"

    return FavoriteGameResponse(
        id=project.id,
        role=role,
        game_name=project.name,
        client_name=project.client_name,
        visibility=project.visibility,
        online_date=project.start_time,
        game_type=project.game_type,
        playing_type=project.playing_type,
        total_players=total_players,
        groups=[
            GroupResponse(
                id=group.id,
                name=group.name,
                managers=await _process_group_managers(group, users, db),
                arenas=[
                    ArenaResponse(
                        id=arena.id,
                        name=arena.name
                    ) for arena in (await get_arenas_by_group(group.id, db))
                ]
            ) for group in (await get_groups_by_game(project.id, db))
        ]
    )


async def fetch_recent_projects(db: AsyncSession, org_id, user_id: str):
    """
    Fetch recent projects for an organization.

    :param db: Database session
    :param org_id: Organization identifier
    :return: List of recent game responses
    """
    recent_projects = await get_recent_projects_by_org_by_user(org_id, user_id, db)

    recent_tasks = [
        await _process_recent_project(db, project, user_id)
        for project in recent_projects
    ]

    return recent_tasks


async def _process_recent_project(db, project, user_id: str):
    """
    Process a single recent project with details.

    :param db: Database session
    :param project: Project model instance
    :return: Recent game response
    """
    total_players = await count_session_players(db, project.module_game_id, project.id)
    ids = await get_manager_id_by_game(project.id, db)
    if len(ids) != 0:
        users = await get_user_service().get_users_by_id(list(ids))
    else:
        users = dict()

    role = await get_user_role_in_game_by_org(project.organisation_code, user_id, project.id, db)
    if role == "player":
        player = await get_player_id_by_game_by_user(project.id, user_id, db)
        if player is not None and player.is_game_master:
            role = "game_master"

    return RecentGameResponse(
        id=project.id,
        role=role,
        game_name=project.name,
        client_name=project.client_name,
        visibility=project.visibility,
        online_date=project.start_time,
        game_type=project.game_type,
        playing_type=project.playing_type,
        total_players=total_players,
        groups=[
            GroupResponse(
                id=group.id,
                name=group.name,
                managers=await _process_group_managers(group, users, db),
                arenas=[
                    ArenaResponse(
                        id=arena.id,
                        name=arena.name
                    ) for arena in (await get_arenas_by_group(group.id, db))
                ]
            ) for group in (await get_groups_by_game(project.id, db))
        ]
    )


async def space_user(db: AsyncSession, user_id: str, org_id: str):
    """
    Comprehensive admin space retrieval with concurrent processing.

    :param db: Database session
    :param user_id: User identifier
    :param org_id: Organization identifier
    :return: AdminSpaceClientResponse
    """
    # Await all concurrent tasks
    # projects, favorite_projects, recent_projects = await asyncio.gather(
    #     projects_coro,
    #     favorite_projects_coro,
    #     recent_projects_coro
    # )

    project = await get_next_game_by_org_by_user(org_id=org_id, user_id=user_id, session=db)
    favorite_projects = await fetch_favorite_projects(db, user_id)
    recent_projects = await fetch_recent_projects(db, org_id, user_id)

    # Process project events
    if project:
        role = await get_user_role_in_game_by_org(org_id, user_id, project.id, db)
        if role == "player":
            player = await get_player_id_by_game_by_user(project.id, user_id, db)
            if player is not None and player.is_game_master:
                role = "game_master"
        events = [await _process_single_event(db, project, role)]
    else:
        events = []

    return AdminSpaceClientResponse(
        events=events,
        favorite_games=favorite_projects,
        recent_games=recent_projects
    )
