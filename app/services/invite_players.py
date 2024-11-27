import re
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models import Project, ArenaSessionPlayers, ArenaSession
from app.enums import EmailStatus
from app.payloads.request.InvitePlayerRequest import InvitePlayerRequest
import logging

from app.services.organisation_service import get_organisation_service
from app.services.send_invite_email import send_invite_email

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Regular expression for validating email (basic format check)
EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"


def is_valid_email(email: str) -> bool:
    """
    Validates an email address using a regular expression.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    return bool(re.match(EMAIL_REGEX, email))


async def invite_players(
        db: Session,
        session: ArenaSession,
        invite_req: InvitePlayerRequest,
        background_tasks: BackgroundTasks,
):
    """
    Invites players to a session by sending email invitations and tracking email status.

    Args:
        db (Session): Database session for querying and persisting data.
        session (ArenaSession): The session to which players are invited.
        invite_req (InvitePlayerRequest): Request containing the players to invite.
        background_tasks (BackgroundTasks): Task runner for sending emails asynchronously.

    Returns:
        dict: Confirmation message indicating emails are queued for sending.
    """
    # Fetch the associated project with validation
    project = db.query(Project).filter(Project.id == session.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found for the session."
        )

    # Construct game and organization details
    game_name = project.name

    if project.organisation_code:
        organisation_name = get_organisation_service().get_organisation_name(str(project.organisation_code))
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisation not found."
        )

    game_link = f"{organisation_name}.gamitool.com/{project.slug}/invite"

    players_to_add: List[ArenaSessionPlayers] = []
    email_set = set()  # To check for duplicate emails in the invite request

    for user in invite_req.members:
        if not user.user_email:
            logger.warning(f"Skipping user with missing email: {user.user_fullname}")
            continue  # Skip if email is not provided

        # Email validation (without external library)
        if not is_valid_email(user.user_email):
            logger.error(f"Invalid email for {user.user_fullname}: {user.user_email}.")
            continue  # Skip invalid emails

        if user.user_email in email_set:
            logger.warning(f"Duplicate email detected: {user.user_email}. Skipping.")
            continue  # Skip duplicate emails
        email_set.add(user.user_email)

        # Check if the player already exists in the session
        existing_player = db.query(ArenaSessionPlayers).filter(
            ArenaSessionPlayers.user_email == user.user_email,
            ArenaSessionPlayers.session_id == session.id
        ).first()

        if existing_player:
            logger.info(f"Player {user.user_fullname} already invited to this session.")
            continue  # Skip if the player is already in the session

        # Add player to list
        db_player = ArenaSessionPlayers(
            session_id=session.id,
            user_name=user.user_fullname,
            user_email=user.user_email,
            user_id=str(user.user_id) if user.user_id else None,
            organisation_code=session.organisation_code,
            email_status=EmailStatus.PENDING,  # Set initial email status to PENDING
        )
        players_to_add.append(db_player)

        # Queue email sending in the background
        background_tasks.add_task(
            send_invite_email,
            db=db,
            player=db_player,
            email=user.user_email,
            fullname=user.user_fullname,
            organisation_name=organisation_name,
            game_name=game_name,
            game_link=game_link,
        )

    # Persist players to the database
    if players_to_add:
        try:
            db.add_all(players_to_add)
            db.commit()
            logger.info(f"{len(players_to_add)} players added to the session.")
        except Exception as db_error:
            logger.error(f"Database error while saving players: {db_error}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while saving players to the session."
            )

    return {"message": f"{len(players_to_add)} players invited. Emails queued for sending."}
