from typing import Optional, List
from uuid import UUID

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.models import ArenaSession
from app.payloads.response.ArenaShowByGameResponse import ArenaShowByGameResponse, ArenaShowByGameSessionResponse, \
    ArenaShowByGameSessionMemberResponse
from app.services.get_arena import get_arena
from app.services.user_service import get_user_service


async def show_arena_by_game(db: Session, arena_id: UUID, game_id: UUID, org_id: str) -> ArenaShowByGameResponse:
    db_arena = get_arena(db, arena_id, org_id)

    if not db_arena:
        raise NoResultFound("Arena not found")

    arena = ArenaShowByGameResponse(id=db_arena.id,
                                    name=db_arena.name,
                                    sessions=[])

    arena_sessions = db.query(ArenaSession).filter(
        ArenaSession.project_id == str(game_id),
        ArenaSession.arena_id == db_arena.id
    ).all()
    print(arena_sessions)

    # Populate sessions
    arena.sessions = await _get_sessions_by_arena(arena_sessions)

    return arena


async def _get_sessions_by_arena(arena_sessions) -> List[ArenaShowByGameSessionResponse]:
    """
    Fetches sessions and their associated players for a given arena.

    Args:
        arena_sessions: Queryset of arena sessions.

    Returns:
        List[GroupByGameArenaSessionResponse]: A list of sessions with nested players.
    """
    sessions = []

    for db_session in arena_sessions:
        # Build session details
        session = ArenaShowByGameSessionResponse(
            id=db_session.id,
            period_type=db_session.period_type,
            start_time=db_session.start_time,
            end_time=db_session.end_time,
            access_status=db_session.access_status,
            session_status=db_session.session_status,
            view_access=db_session.view_access,
            players=(await _get_players_by_session(db_session))
        )

        sessions.append(session)

    return sessions


async def _get_players_by_session(db_session) -> List[ArenaShowByGameSessionMemberResponse]:
    """
    Fetches players for a given session.

    Args:
        db_session: The session object containing players.

    Returns:
        List[GroupByGameSessionPlayerClientResponse]: A list of player responses.
    """
    players = []

    for db_player in db_session.players:
        # Fetch user details using the UserServiceClient
        user_details = None
        if db_player.user_id and db_player.user_id != 'None':
            user_details = await get_user_service().get_user_by_id(db_player.user_id)

        if not user_details and db_player.user_email and db_player.user_email != 'None':
            user_details = await get_user_service().get_user_by_email(db_player.user_email)

        # Build player details
        if user_details:
            player = ArenaShowByGameSessionMemberResponse(
                **dict(user_details)
            )
        else:
            player = ArenaShowByGameSessionMemberResponse(
                user_id=db_player.user_id,
                email=db_player.user_email,
                first_name=db_player.user_name,
                last_name=db_player.user_name
            )

        players.append(player)

    return players


async def _fetch_user_details(user_id: Optional[str], user_email: Optional[str]) -> Optional[dict]:
    """
    Fetches user details by ID or email using the UserServiceClient.

    Args:
        user_id (Optional[str]): The user ID.
        user_email (Optional[str]): The user email.

    Returns:
        Optional[dict]: A dictionary of user details if found, otherwise None.
    """
    user_service = get_user_service()

    if user_id:
        user_details = await user_service.get_user_by_id(user_id)
        if user_details:
            return user_details

    if user_email:
        return await user_service.get_user_by_email(user_email)

    return None
