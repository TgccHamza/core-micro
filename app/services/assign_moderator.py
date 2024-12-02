import logging
import re
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, BackgroundTasks
from app.repositories.get_game_by_id import get_game_by_id
from app.services.get_session import get_session
from app.services.organisation_service import get_organisation_service
from app.services.send_invite_moderator import send_invite_moderator
from app.services.user_service import get_user_service

# Set up logging
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


async def assign_moderator(db: AsyncSession, session_id: str, org_id: str, email: str,
                           background_tasks: BackgroundTasks) -> dict[str, str]:
    try:

        session = await get_session(db, session_id, org_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found."
            )

        # Fetch the associated project with validation
        project = await get_game_by_id(session.project_id, org_id, db)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found for the session."
            )

        # Construct game and organization details
        game_name = project.name

        if project.organisation_code:
            organisation_name = await get_organisation_service().get_organisation_name(str(project.organisation_code))
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organisation not found."
            )

        # Email validation
        if not is_valid_email(email):
            logger.error(f"Invalid email email.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid email email."
            )

        users = await get_user_service().get_users_by_email([email])

        if len(users) == 0:
            user = None
        else:
            user = users[email]

        session.super_game_master_mail = email

        game_link = f"{organisation_name}.gamitool.com/game/{project.id}/moderator/invite?token={session.id}"
        # Queue email sending in the background
        background_tasks.add_task(
            send_invite_moderator,
            db=db,
            session=session,
            email=email,
            fullname=user.full_name if user else "",
            organisation_name=organisation_name,
            game_name=game_name,
            game_link=game_link,
        )

        # Persist players to the database
        try:
            db.add(session)
            await db.commit()
            logger.info(f"Moderator has been assigned the session.")
        except Exception as db_error:
            logger.error(f"Database error while saving players: {db_error}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while saving players to the session."
            )

        return {"message": f"Moderator invited. Emails queued for sending."}

    except Exception as error:
        logger.error(f"Error while assign moderator: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving players to the session."
        )
