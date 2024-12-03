from typing import List, Optional, Dict, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

import logging

from app.repositories.get_arena_by_id import get_arena_by_id
from app.repositories.get_game_by_id import get_game_by_id
from app.repositories.get_group_by_arena import get_group_by_arena
from app.repositories.get_manager_by_group import get_manager_by_group
from app.repositories.get_manager_id_by_group import get_manager_id_by_group
from app.repositories.get_player_id_by_session import get_player_id_by_session
from app.repositories.get_players_by_session import get_players_by_session
from app.repositories.get_session_by_game import get_session_by_game
from app.repositories.get_total_groups_by_game import get_total_groups_by_game
from app.repositories.get_total_managers_by_game import get_total_managers_by_game
from app.repositories.get_total_players_by_game import get_total_players_by_game

logger = logging.getLogger(__name__)

from app.models import ArenaSessionPlayers, ArenaSession, Project, Arena
from app.payloads.response.GameViewClientResponse import GameViewClientResponse, GameViewArenaResponse, \
    GameViewSessionResponse, GameViewSessionPlayerClientResponse, GameViewGroupResponse, GameViewManagerResponse
from app.payloads.response.UserResponse import UserResponse
from app.services.user_service import get_user_service


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


async def _get_managers_by_group(db_session: AsyncSession, group_id: str, users: dict[str, UserResponse]) -> List[
    GameViewManagerResponse]:
    """
    Fetches and enriches managers for a given group with user details.

    Args:
        db_session: The database group object.
        group_id: The group
        users: The users managers

    Returns:
        List[GroupByGameUserClientResponse]: A list of enriched manager responses.
    """
    managers = []
    db_managers = await get_manager_by_group(group_id, db_session)

    for db_manager in db_managers:
        user_details = users.get(db_manager.user_id, None)
        manager_response = GameViewManagerResponse(
            id=str(db_manager.id) if db_manager.id else None,
            user_id=user_details.get("user_id") if user_details else db_manager.user_id,
            user_email=user_details.get("user_email") if user_details else db_manager.user_email,
            first_name=user_details.get("first_name") if user_details else db_manager.first_name,
            last_name=user_details.get("last_name") if user_details else db_manager.last_name,
        )

        managers.append(manager_response)

    return managers

async def _process_session_players(players: Sequence[ArenaSessionPlayers], users: dict[str, UserResponse]) -> List[GameViewSessionPlayerClientResponse]:
    """
    Process players for a given session with enhanced user detail retrieval.

    Args:
        users (ArenaSession): Arena session

    Returns:
        List[GameViewSessionPlayerClientResponse]: Processed player details
    """
    # Fetch all user details concurrently
    processed_players = []

    print("=================================")
    print(users)
    for player in players:
        user_detail = users.get(player.user_id, None)
        processed_player = GameViewSessionPlayerClientResponse(
            user_id=user_detail.get('user_id') if user_detail else str(player.user_id),
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
        db: AsyncSession
) -> GameViewSessionResponse:
    """
    Create detailed session response with processed players.

    Args:
        session (ArenaSession): Arena session
        db (Session): Database session

    Returns:
        GameViewSessionResponse: Structured session response
    """
    players = await get_players_by_session(session.id, db)
    ids = await get_player_id_by_session(session.id, db)
    if len(ids) != 0:
        users = await get_user_service().get_users_by_id(list(ids))
    else:
        users = list()

    return GameViewSessionResponse(
        id=session.id,
        period_type=session.period_type,
        start_time=session.start_time,
        end_time=session.end_time,
        access_status=session.access_status,
        session_status=session.session_status,
        view_access=session.view_access,
        players=await _process_session_players(players, users)
    )


# Modify the _build_game_arenas function to pass db session
async def _build_game_arenas(
        db: AsyncSession,
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
    arena_map: Dict[str, GameViewArenaResponse] = {}
    arena_sessions = await get_session_by_game(game.id, db)
    for arena_session in arena_sessions:
        db_arena = await get_arena_by_id(arena_session.arena_id, db)
        if not db_arena:
            continue
        arena_id = db_arena.id

        # Initialize arena response if not exists
        if arena_id not in arena_map:
            arena_map[arena_id] = await _create_arena_response(db_arena, db)

        # Add session to arena (pass db session)
        arena_map[arena_id].sessions.append(
            await _create_session_response(arena_session, db)
        )

    return list(arena_map.values())


# Update the main gameView function to pass db session to child functions
async def gameView(
        db: AsyncSession,
        org_id: str,
        game_id: str
) -> GameViewClientResponse:
    """
    Retrieve comprehensive game view with optional detailed information.

    Args:
        db (AsyncSession): Database session
        org_id (str): Organization identifier
        game_id (str): Game identifier

    Returns:
        GameViewClientResponse: Comprehensive game view

    Raises:
        HTTPException: If game is not found
    """
    # Fetch game with optimized query
    game = await get_game_by_id(game_id, org_id, db)

    # Compute aggregated metrics
    metrics = await _compute_game_metrics(db, game_id)

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


async def _compute_game_metrics(
        db: AsyncSession,
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
        'total_managers': (await get_total_managers_by_game(game_id, db)),
        'total_groups': (await get_total_groups_by_game(game_id, db)),
        'total_players': (await get_total_players_by_game(game_id, db)),
    }


async def _create_arena_response(
        arena: Arena, db: AsyncSession
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
    group = await get_group_by_arena(arena.id, db)
    if group:
        first_group = group
        manager_ids = await get_manager_id_by_group(first_group.id, db)
        if len(manager_ids) > 0:
            users = await get_user_service().get_users_by_id(list(manager_ids))
        else:
            users = list()
        arena_resp.group = GameViewGroupResponse(
            id=first_group.id,
            name=first_group.name,
            managers=await _get_managers_by_group(db, first_group.id, users)
        )

    return arena_resp
