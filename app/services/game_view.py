import asyncio
from typing import List, Optional, Dict

from fastapi import HTTPException
from sqlalchemy.orm import Session

import logging
logger = logging.getLogger(__name__)

from app.models import ArenaSessionPlayers, ArenaSession, Project, Arena, GroupUsers, Group, GroupProjects
from app.payloads.response.GameViewClientResponse import GameViewClientResponse, GameViewArenaResponse, \
    GameViewSessionResponse, GameViewSessionPlayerClientResponse, GameViewGroupResponse, GameViewManagerResponse
from app.payloads.response.UserResponse import UserResponse
from app.services.user_service import get_user_service


def _fetch_game_with_relations(
        db: Session,
        org_id: str,
        game_id: str
) -> Project:
    """
    Fetch game with eager loading of related data.

    Args:
        db (Session): Database session
        org_id (str): Organization identifier
        game_id (int): Game identifier

    Returns:
        models.Project: Game with loaded relations

    Raises:
        HTTPException: If game is not found
    """
    game = (
        db.query(Project)
        .filter(
            Project.organisation_code == org_id,
            Project.id == game_id
        )
        .first()
    )

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    return game


def _parse_tags(tags: Optional[str]) -> List[str]:
    """
    Parse and clean tags.

    Args:
        tags (Optional[str]): Comma-separated tags

    Returns:
        List[str]: Cleaned tags
    """
    return [
        tag.strip()
        for tag in (tags or '').split(',')
        if tag.strip()
    ]


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
) -> List[GameViewManagerResponse]:
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
        processed_manager = GameViewManagerResponse(
            user_id=user_detail.get('user_id') if user_detail else manager.user_id,
            email=user_detail.get('user_email') if user_detail else manager.user_email,
            first_name=user_detail.get('first_name') if user_detail else None,
            last_name=user_detail.get('last_name') if user_detail else None,
            picture=user_detail.get('picture') if user_detail else None
        )

        processed_managers.append(processed_manager)

    return processed_managers



async def _process_session_players(session: ArenaSession) -> List[GameViewSessionPlayerClientResponse]:
    """
    Process players for a given session with enhanced user detail retrieval.

    Args:
        session (ArenaSession): Arena session

    Returns:
        List[GameViewSessionPlayerClientResponse]: Processed player details
    """
    # Fetch all user details concurrently
    user_details = await _fetch_users_concurrently(session.players)

    processed_players = []

    for player, user_detail in zip(session.players, user_details):
        processed_player = GameViewSessionPlayerClientResponse(
            user_id=user_detail.get('user_id') if user_detail else player.user_id,
            email=user_detail.get('user_email') if user_detail else player.user_email,
            first_name=user_detail.get('first_name') if user_detail else None,
            last_name=user_detail.get('last_name') if user_detail else None,
            picture=user_detail.get('picture') if user_detail else None
        )

        processed_players.append(processed_player)

    return processed_players



# Update the session response creation in the previous function
async def _create_session_response(
        session: ArenaSession,
        db: Session
) -> GameViewSessionResponse:
    """
    Create detailed session response with processed players.

    Args:
        session (ArenaSession): Arena session
        db (Session): Database session

    Returns:
        GameViewSessionResponse: Structured session response
    """
    return GameViewSessionResponse(
        id=session.id,
        period_type=session.period_type,
        start_time=session.start_time,
        end_time=session.end_time,
        access_status=session.access_status,
        session_status=session.session_status,
        view_access=session.view_access,
        players=await _process_session_players(session)
    )


# Modify the _build_game_arenas function to pass db session
async def _build_game_arenas(
        db: Session,
        game: Project
) -> List[GameViewArenaResponse]:
    """
    Build detailed arenas with sessions and groups.

    Args:
        db (Session): Database session
        game (Project): Game instance

    Returns:
        List[GameViewArenaResponse]: Detailed arena responses
    """
    arena_map: Dict[int, GameViewArenaResponse] = {}

    for arena_session in game.arena_sessions:
        if not arena_session.arena:
            continue
        arena_id = arena_session.arena.id

        # Initialize arena response if not exists
        if arena_id not in arena_map:
            arena_map[arena_id] = await _create_arena_response(arena_session.arena)

        # Add session to arena (pass db session)
        arena_map[arena_id].sessions.append(
            await _create_session_response(arena_session, db)
        )

    return list(arena_map.values())


# Update the main gameView function to pass db session to child functions
async def gameView(
        db: Session,
        org_id: str,
        game_id: str
) -> GameViewClientResponse:
    """
    Retrieve comprehensive game view with optional detailed information.

    Args:
        db (Session): Database session
        org_id (str): Organization identifier
        game_id (str): Game identifier
        detailed (bool, optional): Flag to fetch additional details. Defaults to False.

    Returns:
        GameViewClientResponse: Comprehensive game view

    Raises:
        HTTPException: If game is not found
    """
    # Fetch game with optimized query
    game = _fetch_game_with_relations(db, org_id, game_id)

    # Compute aggregated metrics
    metrics = _compute_game_metrics(db, game_id)

    # Build arenas with sessions and groups (pass db session)
    arenas = await _build_game_arenas(db, game)

    # Prepare response
    return GameViewClientResponse(
        id=game.id,
        game_name=game.name,
        client_name=game.client_name,
        description=game.description,
        visibility=game.visibility,
        online_date=game.start_time,
        end_date=game.end_time,
        game_type=game.game_type,
        playing_type=game.playing_type,
        total_managers=metrics['total_managers'],
        total_groups=metrics['total_groups'],
        total_players=metrics['total_players'],
        arenas=arenas,
        tags=_parse_tags(game.tags)
    )


def _compute_game_metrics(
        db: Session,
        game_id: str
) -> Dict[str, int]:
    """
    Compute game-level metrics efficiently.

    Args:
        db (Session): Database session
        game_id (int): Game identifier

    Returns:
        Dict[str, int]: Game metrics
    """
    return {
        'total_managers': (
            db.query(GroupUsers)
            .join(Group, Group.id == GroupUsers.group_id)
            .join(GroupProjects, Group.id == GroupProjects.group_id)
            .filter(GroupProjects.project_id == game_id)
            .distinct(GroupUsers.user_id)
            .count()
        ),
        'total_groups': (
            db.query(GroupProjects)
            .filter(GroupProjects.project_id == game_id)
            .count()
        ),
        'total_players': (
            db.query(ArenaSessionPlayers)
            .join(ArenaSession, ArenaSession.id == ArenaSessionPlayers.session_id)
            .filter(ArenaSession.project_id == game_id)
            .count()
        )
    }


async def _create_arena_response(
        arena: Arena
) -> GameViewArenaResponse:
    """
    Create arena response with group details.

    Args:``
        arena (models.Arena): Arena instance

    Returns:
        GameViewArenaResponse: Structured arena response
    """
    arena_resp = GameViewArenaResponse(
        id=arena.id,
        name=arena.name,
        sessions=[]
    )

    if arena.groups:
        first_group = arena.groups[0]
        arena_resp.group = GameViewGroupResponse(
            id=first_group.id,
            name=first_group.name,
            managers=await _process_group_managers(first_group)
        )

    return arena_resp
