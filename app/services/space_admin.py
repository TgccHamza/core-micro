import asyncio
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
from app.models import Project, ArenaSession, ArenaSessionPlayers, ProjectFavorite, Group, GroupUsers
from app.payloads.response.EspaceAdminClientResponse import ArenaResponse, ManagerResponse, GroupResponse, \
    RecentGameResponse, FavoriteGameResponse, EventGameResponse, AdminSpaceClientResponse
from app.payloads.response.UserResponse import UserResponse
from app.services.user_service import get_user_service


async def _fetch_user_details(user_id: str, user_email: str) -> UserResponse | None:
    if user_id and user_id != 'None':
        try:
            return await get_user_service().get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error fetching user by ID {user_id}: {str(e)}")
    elif user_email and user_email != 'None':
        try:
            return await get_user_service().get_user_by_email(user_email)
        except Exception as e:
            logger.error(f"Error fetching user by email {user_email}: {str(e)}")
    return None


async def _fetch_users_concurrently(users: List[ArenaSessionPlayers | GroupUsers]) -> List[Optional[UserResponse]]:
    """
    Fetch user details concurrently for multiple players.

    Args:
        players (List[ArenaSessionPlayers]): List of players to fetch details for

    Returns:
        List[Optional[UserResponse]]: List of user details
    """
    # Create tasks for concurrent user detail fetching
    fetch_tasks = [
        _fetch_user_details(user.user_id, user.user_email)
        for user in users
    ]

    # Wait for all tasks to complete
    return await asyncio.gather(*fetch_tasks)


async def _process_group_managers(
        db_group: Group
) -> List[ManagerResponse]:
    """
    Process group managers with concurrent user details fetching.

    Args:
        db_group (Group): Group

    Returns:
        List[GameViewManagerResponse]: Processed manager details
    """
    # Fetch all manager details concurrently
    manager_details = await _fetch_users_concurrently(db_group.managers)

    processed_managers = []

    for manager, user_detail in zip(db_group.managers, manager_details):
        processed_manager = ManagerResponse(
            user_id=user_detail.get('user_id') if user_detail else str(manager.user_id),
            email=user_detail.get('user_email') if user_detail else manager.user_email,
            first_name=user_detail.get('first_name') if user_detail else None,
            last_name=user_detail.get('last_name') if user_detail else None,
            picture=user_detail.get('picture') if user_detail else None
        )

        processed_managers.append(processed_manager)

    return processed_managers


def fetch_project_details(db: Session, org_id: str, current_time):
    """
    Fetch project details for a given organization within the next month.

    :param db: Database session
    :param org_id: Organization identifier
    :param current_time: Current timestamp
    :return: List of project events
    """
    one_month_later = current_time + timedelta(days=31)
    return _fetch_projects_by_criteria(db,
                                       org_id,
                                       current_time,
                                       one_month_later)


def _fetch_projects_by_criteria(db: Session, org_id: str, current_time, one_month_later):
    """
    Synchronous database query for projects.

    :return: List of projects matching criteria
    """
    return db.query(Project).filter(
        Project.organisation_code == org_id,
        Project.start_time >= current_time,
        Project.start_time <= one_month_later
    ).all()


def fetch_total_players(db: Session, module_game_id):
    """
    Fetch total number of players for a specific module game.

    :param db: Database session
    :param module_game_id: Module game identifier
    :return: Total number of players
    """
    return _count_session_players(db, module_game_id)


def _count_session_players(db: Session, module_game_id):
    """
    Synchronous player count query.

    :return: Total number of players
    """
    return db.query(ArenaSessionPlayers).join(
        ArenaSession, ArenaSession.id == ArenaSessionPlayers.session_id
    ).filter(
        ArenaSession.player_module_id == module_game_id
    ).count()


def process_project_events(db: Session, projects):
    """
    Process project events with concurrent player counting.

    :param db: Database session
    :param projects: List of projects
    :return: List of processed events
    """
    events_tasks = [
        _process_single_event(db, project)
        for project in projects
    ]
    return events_tasks


async def _process_single_event(db: Session, project):
    """
    Process a single project event with player count.

    :param db: Database session
    :param project: Project model instance
    :return: Processed event response
    """
    total_players = fetch_total_players(db, project.module_game_id)

    return EventGameResponse(
        id=project.id,
        game_name=project.name,
        client_name=project.client_name,
        visibility=project.visibility,
        online_date=project.start_time,
        game_type=project.game_type,
        playing_type=project.playing_type,
        total_players=total_players,
        tags=[x.strip() for x in project.tags.split(",")]
    )


def fetch_favorite_projects(db: Session, user_id: str):
    """
    Fetch and process favorite projects for a user.

    :param db: Database session
    :param user_id: User identifier
    :return: List of favorite game responses
    """
    favorite_projects = db.query(ProjectFavorite).filter(
        ProjectFavorite.user_id == user_id
    ).all()

    favorite_tasks = [
        _process_favorite_project(db, fav_project)
        for fav_project in favorite_projects
    ]

    return favorite_tasks


async def _process_favorite_project(db: Session, favorite_project):
    """
    Process a single favorite project with details.

    :param db: Database session
    :param favorite_project: Favorite project model instance
    :return: Favorite game response
    """
    project = favorite_project.project
    total_players = fetch_total_players(db, project.module_game_id)

    return FavoriteGameResponse(
        id=project.id,
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
                managers=await _process_group_managers(group),
                arenas=[
                    ArenaResponse(
                        id=arena.id,
                        name=arena.name
                    ) for arena in group.arenas
                ]
            ) for group in project.groups
        ]
    )


def fetch_recent_projects(db: Session, org_id):
    """
    Fetch recent projects for an organization.

    :param db: Database session
    :param org_id: Organization identifier
    :return: List of recent game responses
    """
    recent_projects = db.query(Project).filter(
        Project.organisation_code == org_id
    ).order_by(Project.created_at.desc()).limit(5).all()

    recent_tasks = [
        _process_recent_project(db, project)
        for project in recent_projects
    ]

    return recent_tasks


async def _process_recent_project(db, project):
    """
    Process a single recent project with details.

    :param db: Database session
    :param project: Project model instance
    :return: Recent game response
    """
    total_players = fetch_total_players(db, project.module_game_id)

    return RecentGameResponse(
        id=project.id,
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
                managers=await _process_group_managers(group),
                arenas=[
                    ArenaResponse(
                        id=arena.id,
                        name=arena.name
                    ) for arena in group.arenas
                ]
            ) for group in project.groups
        ]
    )


async def space_admin(db: Session, user_id: str, org_id: str):
    """
    Comprehensive admin space retrieval with concurrent processing.

    :param db: Database session
    :param user_id: User identifier
    :param org_id: Organization identifier
    :return: AdminSpaceClientResponse
    """
    current_time = datetime.now()

    # Concurrent fetching of projects, favorite projects, and recent projects
    projects_coro = fetch_project_details(db, org_id, current_time)
    favorite_projects_coro = fetch_favorite_projects(db, user_id)
    recent_projects_coro = fetch_recent_projects(db, org_id)

    # Await all concurrent tasks
    # projects, favorite_projects, recent_projects = await asyncio.gather(
    #     projects_coro,
    #     favorite_projects_coro,
    #     recent_projects_coro
    # )

    projects = projects_coro
    favorite_projects = await asyncio.gather(*favorite_projects_coro)
    recent_projects = await asyncio.gather(*recent_projects_coro)

    # Process project events
    events = await asyncio.gather(*process_project_events(db, projects))

    return AdminSpaceClientResponse(
        events=events,
        favorite_games=favorite_projects,
        recent_games=recent_projects
    )
