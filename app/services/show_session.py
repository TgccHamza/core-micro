import logging
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from app.models import ArenaSession

from app.payloads.response.SessionResponse import SessionPlayerClientResponse, ArenaGroupUserResponse, ArenaResponse, \
    ArenaGroupResponse, ProjectResponse, SessionResponse
from app.services.get_session import get_session
from app.services.user_service import get_user_service

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def show_session(db: Session, session_id: str, org_id: str) -> SessionResponse:
    try:

        session = get_session(db, session_id, org_id)
        return await map_session_to_response(session)

    except SQLAlchemyError as e:
        # Handle any database-related errors
        logger.error(
            f"Database error occurred while retrieving session {session_id} for organization {org_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the session."
        )

    except Exception as e:
        # Handle any other unexpected errors
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the session."
        )


async def map_session_to_response(session: ArenaSession) -> SessionResponse:
    """
    Maps a single ArenaSession to a SessionResponse.
    """
    return SessionResponse(
        id=session.id,
        arena_id=session.arena_id,
        project_id=session.project_id,
        period_type=session.period_type,
        start_time=session.start_time,
        end_time=session.end_time,
        access_status=session.access_status,
        session_status=session.session_status,
        view_access=session.view_access,
        project=map_project(session.project),
        arena=await _map_arena(session.arena),
        players=await _map_players(session.players)
    )


def map_project(project) -> ProjectResponse | None:
    """
    Maps the Project model to ProjectResponse.
    """
    if not project:
        return None

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        db_index=project.db_index,
        slug=project.slug,
        visibility=project.visibility,
        activation_status=project.activation_status,
        client_id=project.client_id,
        client_name=project.client_name,
        start_time=project.start_time,
        end_time=project.end_time
    )


async def _map_arena(arena) -> ArenaResponse | None:
    """
    Maps the Arena model to ArenaResponse.
    """
    if not arena:
        return None

    return ArenaResponse(
        id=arena.id,
        name=arena.name,
        groups=[await _map_arena_group(group) for group in arena.groups]
    )


async def _map_arena_group(group) -> ArenaGroupResponse:
    """
    Maps ArenaGroup model to ArenaGroupResponse.
    """
    return ArenaGroupResponse(
        id=group.id,
        name=group.name,
        managers=[await _map_group_manager(user) for user in group.managers]
    )


async def _map_group_manager(user) -> ArenaGroupUserResponse:
    user_details = None
    if user.user_id and user.user_id != 'None':
        user_details = await get_user_service().get_user_by_id(user.user_id)

    if not user_details and user.user_email and user.user_email != 'None':
        user_details = await get_user_service().get_user_by_email(user.user_email)

    # Build player details
    if user_details:
        player = ArenaGroupUserResponse(
            **dict(user_details)
        )
    else:
        player = ArenaGroupUserResponse(
            user_id=user.user_id,
            email=user.user_email,
            first_name=user.first_name,
            last_name=user.last_name
        )
    """
    Maps ArenaGroup model to ArenaGroupResponse.
    """
    return player


async def _map_players(players) -> List[SessionPlayerClientResponse]:
    """
    Maps players in the session to SessionPlayerClientResponse.
    """
    return [
        await _map_player(player)
        for player in players
    ]


async def _map_player(user) -> SessionPlayerClientResponse:
    user_details = None
    if user.user_id and user.user_id != 'None':
        user_details = await get_user_service().get_user_by_id(user.user_id)

    if not user_details and user.user_email and user.user_email != 'None':
        user_details = await get_user_service().get_user_by_email(user.user_email)

    # Build player details
    if user_details:
        player = SessionPlayerClientResponse(
            id=user.id,
            **dict(user_details),
            email_status=user.email_status
        )
    else:
        player = SessionPlayerClientResponse(
            id=user.id,
            user_id=user.user_id,
            user_email=user.user_email,
            user_name=user.user_name,
            email_status=user.email_status
        )
    return player


def handle_db_error(org_id: str, error: SQLAlchemyError):
    """
    Handles errors related to database operations.
    """
    raise SQLAlchemyError(f"Error retrieving sessions for organisation {org_id}: {str(error)}")


def handle_unexpected_error(error: Exception):
    """
    Handles any unexpected errors that occur.
    """
    raise Exception(f"Unexpected error occurred while retrieving sessions: {str(error)}")


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
