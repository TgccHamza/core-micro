import logging
import os
import re

from httpx import AsyncClient, RequestError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArenaSessionPlayers, ArenaSession
from app.enums import EmailStatus

# Configure logger for structured logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def send_invite_moderator(
        db: AsyncSession,
        session: ArenaSession,
        email: str,
        fullname: str,
        organisation_name: str,
        game_name: str,
        game_link: str,
):
    """
    Sends an invitation email to a player and updates their email status in the database.

    Args:
        db (Session): Database session for updating player email status.
        session (ArenaSession): Moderator database object to update email status.
        email (str): The recipient's email address.
        fullname (str): The recipient's full name.
        organisation_name (str): The organization's name sending the invitation.
        game_name (str): The game's name.
        game_link (str): The invitation link to the game.

    Returns:
        None
    """
    email_service_url = f"{os.getenv('URL_MAILER')}/api/v1/emails"

    if fullname is None:
        fullname = ""
    # Get the path to the template file
    template_path = os.path.join('/app/app', "mails", "template_invite_moderator.html")

    # Read the template
    with open(template_path, "r", encoding="utf-8") as file:
        template_content = file.read()

    # Replace placeholders with actual values
    template_content = template_content.replace("[Recipient Name]", fullname)
    template_content = template_content.replace("[OrgName]", organisation_name)
    template_content = template_content.replace("[Your CTA URL]", game_link)
    template_content = template_content.replace("[GAME_NAME]", game_name)
    template_content = re.sub(r"\s+", " ", template_content).strip()

    email_payload = {
        "html_body": template_content,
        "is_html": True,
        "subject": f"{organisation_name} - Invitation to play {game_name}",
        "to": email,
    }

    try:
        async with AsyncClient() as client:
            response = await client.post(email_service_url, json=email_payload)

        # Update email status based on response
        if response.status_code in {200, 201, 202}:
            logger.info(f"Email sent successfully to {email}. Response Code: {response.status_code}")
            session.email_status = EmailStatus.SENT
        else:
            logger.error(
                f"Failed to send email to {email}. Response Code: {response.status_code}, "
                f"Details: {response.text}"
            )
            session.email_status = EmailStatus.FAILED

    except RequestError as http_err:
        logger.error(f"HTTP request failed for {email}: {http_err}")
        session.email_status = EmailStatus.FAILED

    except Exception as general_err:
        logger.critical(f"Unexpected error for {email}: {general_err}")
        session.email_status = EmailStatus.FAILED

    finally:
        try:
            await db.commit()
        except Exception as db_err:
            logger.critical(f"Failed to commit changes to the database: {db_err}")
            raise
