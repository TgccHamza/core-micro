from typing import List, Optional, Dict, Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

import logging

from app.enums import ModuleForType
from app.payloads.response.GameViewModeratorClientResponse import GameViewModeratorClientResponse, \
    GameViewModeratorSessionResponse, GameViewModeratorSessionPlayerClientResponse, GameViewModeratorArenaResponse, \
    ModeratorModuleLinkResponse
from app.payloads.response.GameViewPlayerClientResponse import GameViewPlayerClientResponse, \
    GameViewPlayerSessionResponse, GameViewPlayerArenaResponse, PlayerModuleLinkResponse
from app.repositories.get_arena_by_id import get_arena_by_id
from app.repositories.get_game_by_id import get_game_by_id
from app.repositories.get_group_by_arena import get_group_by_arena
from app.repositories.get_manager_by_group import get_manager_by_group
from app.repositories.get_manager_email_by_group import get_manager_email_by_group
from app.repositories.get_module_by_game_by_type import get_module_by_game_by_type
from app.repositories.get_player_email_by_session import get_player_email_by_session
from app.repositories.get_player_for_session_by_email import get_player_for_session_by_email
from app.repositories.get_players_by_session import get_players_by_session
from app.repositories.get_session_by_game import get_session_by_game
from app.repositories.get_session_by_game_for_moderator import get_session_by_game_for_moderator
from app.repositories.get_session_by_game_for_player import get_session_by_game_for_player
from app.repositories.get_user_role_in_game_by_org import get_user_role_in_game_by_org

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


async def _process_session_players(players: Sequence[ArenaSessionPlayers], users: dict[str, UserResponse]) -> List[
    GameViewSessionPlayerClientResponse]:
    """
    Process players for a given session with enhanced user detail retrieval.

    Args:
        users (ArenaSession): Arena session

    Returns:
        List[GameViewSessionPlayerClientResponse]: Processed player details
    """
    # Fetch all user details concurrently
    processed_players = []

    for player in players:
        user_detail = users.get(player.user_email, None)
        processed_player = GameViewSessionPlayerClientResponse(
            user_id=user_detail.get('user_id') if user_detail else str(player.user_id),
            email=user_detail.get('user_email') if user_detail else player.user_email,
            first_name=user_detail.get('first_name') if user_detail else None,
            last_name=user_detail.get('last_name') if user_detail else None,
            picture=user_detail.get('picture') if user_detail else None,
            is_game_master = player.is_game_master if player.is_game_master is not None else False
        )

        processed_players.append(processed_player)

    return processed_players


async def _process_session_players_for_moderator(players: Sequence[ArenaSessionPlayers],
                                                 users: dict[str, UserResponse]) -> List[
    GameViewModeratorSessionPlayerClientResponse]:
    """
    Process players for a given session with enhanced user detail retrieval.

    Args:
        users (ArenaSession): Arena session

    Returns:
        List[GameViewSessionPlayerClientResponse]: Processed player details
    """
    # Fetch all user details concurrently
    processed_players = []

    for player in players:
        user_detail = users.get(player.user_email, None)
        processed_player = GameViewModeratorSessionPlayerClientResponse(
            user_id=user_detail.get('user_id') if user_detail else str(player.user_id),
            email=user_detail.get('user_email') if user_detail else player.user_email,
            first_name=user_detail.get('first_name') if user_detail else None,
            last_name=user_detail.get('last_name') if user_detail else None,
            picture=user_detail.get('picture') if user_detail else None,
            is_game_master = player.is_game_master if player.is_game_master is not None else False
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
    emails = await get_player_email_by_session(session.id, db)
    if len(emails) != 0:
        users = await get_user_service().get_users_by_email(list(emails))
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
        db_index=session.db_index,
        players=await _process_session_players(players, users)
    )


# Update the session response creation in the previous function
async def _create_session_for_moderator_response(
        session: ArenaSession,
        db: AsyncSession
) -> GameViewModeratorSessionResponse:
    """
    Create detailed session response with processed players.

    Args:
        session (ArenaSession): Arena session
        db (Session): Database session

    Returns:
        GameViewSessionResponse: Structured session response
    """

    db_arena = await get_arena_by_id(session.arena_id, db)

    players = await get_players_by_session(session.id, db)
    emails = await get_player_email_by_session(session.id, db)
    if len(emails) != 0:
        users = await get_user_service().get_users_by_email(list(emails))
    else:
        users = list()
    links = await get_module_by_game_by_type(session.project_id, [ModuleForType.ALL, ModuleForType.MODERATOR], db)
    return GameViewModeratorSessionResponse(
        id=session.id,
        arena=GameViewModeratorArenaResponse(
            id=db_arena.id,
            name=db_arena.name,
        ) if db_arena else None,
        period_type=session.period_type,
        db_index=session.db_index,
        start_time=session.start_time,
        end_time=session.end_time,
        access_status=session.access_status,
        session_status=session.session_status,
        view_access=session.view_access,
        links=(ModeratorModuleLinkResponse(name=link.name, template_code=link.template_code) for link in links),
        players=await _process_session_players_for_moderator(players, users)
    )


# Update the session response creation in the previous function
async def _create_session_for_player_response(
        session: ArenaSession,
        user_email: str,
        db: AsyncSession
) -> GameViewPlayerSessionResponse:
    """
    Create detailed session response with processed players.

    Args:
        session (ArenaSession): Arena session
        db (Session): Database session

    Returns:
        GameViewSessionResponse: Structured session response
    """

    db_arena = await get_arena_by_id(session.arena_id, db)
    player = await get_player_for_session_by_email(session.id, user_email, db)

    if player.is_game_master:
        links = await get_module_by_game_by_type(session.project_id, [ModuleForType.ALL, ModuleForType.GAMEMASTER], db)
    else:
        links = await get_module_by_game_by_type(session.project_id, [ModuleForType.ALL, ModuleForType.PLAYER], db)

    return GameViewPlayerSessionResponse(
        id=session.id,
        period_type=session.period_type,
        start_time=session.start_time,
        end_time=session.end_time,
        db_index=session.db_index,
        arena=GameViewPlayerArenaResponse(
            id=db_arena.id,
            name=db_arena.name,
        ) if db_arena else None,
        links=(PlayerModuleLinkResponse(name=link.name, template_code=link.template_code) for link in links),
        access_status=session.access_status,
        session_status=session.session_status,
        view_access=session.view_access,
        is_game_master=player.is_game_master if player.is_game_master is not None else False
    )


# Modify the _build_game_arenas function to pass db session
async def _build_game_arenas(user_email: str,
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
    # arena_sessions = await get_session_by_game_for_player(game.id, user_email, db)
    # arena_sessions = await get_session_by_game_for_moderator(game.id, user_email, db)

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


# Modify the _build_game_arenas function to pass db session
async def _build_game_sessions_for_moderator(user_email: str,
                                             db: AsyncSession,
                                             game: Project
                                             ) -> List[GameViewModeratorSessionResponse]:
    """
    Build detailed arenas with sessions and groups.

    Args:
        db (Session): Database session
        game (Project): Game instance

    Returns:
        List[GameViewSessionResponse]: Detailed arena responses
    """

    arena_sessions = await get_session_by_game_for_moderator(game.id, user_email, db)
    sessions = []
    for arena_session in arena_sessions:
        sessions.append(
            await _create_session_for_moderator_response(arena_session, db)
        )

    return sessions


# Modify the _build_game_arenas function to pass db session
async def _build_game_sessions_for_player(user_email: str,
                                          db: AsyncSession,
                                          game: Project
                                          ) -> List[GameViewPlayerSessionResponse]:
    """
    Build detailed arenas with sessions and groups.

    Args:
        db (Session): Database session
        game (Project): Game instance

    Returns:
        List[GameViewSessionResponse]: Detailed arena responses
    """

    arena_sessions = await get_session_by_game_for_player(game.id, user_email, db)
    sessions = []
    for arena_session in arena_sessions:
        sessions.append(
            await _create_session_for_player_response(arena_session, user_email, db)
        )

    return sessions


# Update the main gameView function to pass db session to child functions
async def _build_game_view_manager(
        db: AsyncSession,
        org_id: str,
        user_email: str,
        game_id: str):
    # Fetch game with optimized query
    game = await get_game_by_id(game_id, org_id, db)

    # Build arenas with sessions and groups (pass db session)
    arenas = await _build_game_arenas(user_email, db, game)

    # Prepare response
    return GameViewClientResponse(
        id=game.id,
        role='manager',
        game_name=game.name,
        client_name=game.client_name,
        description=game.description,
        visibility=game.visibility,
        online_date=game.start_time,
        end_date=game.end_time,
        game_type=game.game_type,
        playing_type=game.playing_type,
        arenas=arenas,
        tags=_parse_tags(game.tags)
    )


async def _build_game_view_moderator(
        db: AsyncSession,
        org_id: str,
        user_email: str,
        game_id: str):
    # Fetch game with optimized query
    game = await get_game_by_id(game_id, org_id, db)

    # Build arenas with sessions and groups (pass db session)
    sessions = await _build_game_sessions_for_moderator(user_email, db, game)

    # Prepare response
    return GameViewModeratorClientResponse(
        id=game.id,
        game_name=game.name,
        client_name=game.client_name,
        description=game.description,
        visibility=game.visibility,
        online_date=game.start_time,
        end_date=game.end_time,
        game_type=game.game_type,
        playing_type=game.playing_type,
        sessions=sessions,
        tags=_parse_tags(game.tags)
    )


async def _build_game_view_player(
        db: AsyncSession,
        org_id: str,
        user_email: str,
        game_id: str) -> GameViewPlayerClientResponse:
    game = await get_game_by_id(game_id, org_id, db)

    # Build arenas with sessions and groups (pass db session)
    sessions = await _build_game_sessions_for_player(user_email, db, game)

    # Prepare response
    return GameViewPlayerClientResponse(
        id=game.id,
        game_name=game.name,
        client_name=game.client_name,
        description=game.description,
        visibility=game.visibility,
        online_date=game.start_time,
        end_date=game.end_time,
        game_type=game.game_type,
        playing_type=game.playing_type,
        sessions=sessions,
        tags=_parse_tags(game.tags)
    )


async def gameViewUser(
        db: AsyncSession,
        org_id: str,
        user_email: str,
        game_id: str
) -> GameViewClientResponse | GameViewModeratorClientResponse | GameViewPlayerClientResponse:
    """
    Retrieve comprehensive game view with optional detailed information.

    Args:
        db (AsyncSession): Database session
        org_id (str): Organization identifier
        user_email (str): Email identifier
        game_id (str): Game identifier

    Returns:
        GameViewClientResponse: Comprehensive game view

    Raises:
        HTTPException: If game is not found
    """
    role = await get_user_role_in_game_by_org(org_id, user_email, game_id, db)
    if role is None:
        raise HTTPException(status_code=400, detail="You dont have access for this game")

    if role == 'manager':
        return await _build_game_view_manager(db, org_id, user_email, game_id)
    elif role == 'player':
        return await _build_game_view_player(db, org_id, user_email, game_id)
    else:
        return await _build_game_view_moderator(db, org_id, user_email, game_id)


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
        manager_emails = await get_manager_email_by_group(first_group.id, db)
        if len(manager_emails) > 0:
            users = await get_user_service().get_users_by_email(list(manager_emails))
        else:
            users = list()
        arena_resp.group = GameViewGroupResponse(
            id=first_group.id,
            name=first_group.name,
            managers=await _get_managers_by_group(db, first_group.id, users)
        )

    return arena_resp
