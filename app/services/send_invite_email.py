import logging
from httpx import AsyncClient, RequestError
from sqlalchemy.orm import Session
from app.models import ArenaSessionPlayers
from app.enums import EmailStatus


# Configure logger for structured logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def send_invite_email(
    db: Session,
    player: ArenaSessionPlayers,
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
        player (ArenaSessionPlayers): Player database object to update email status.
        email (str): The recipient's email address.
        fullname (str): The recipient's full name.
        organisation_name (str): The organization's name sending the invitation.
        game_name (str): The game's name.
        game_link (str): The invitation link to the game.

    Returns:
        None
    """
    email_service_url = "https://dev-api.thegamechangercompany.io/mailer/api/v1/emails"
    email_payload = {
        "html_body": (
            f"Hi {fullname},<br/><br/>"
            f"You have been invited by {organisation_name} to play {game_name}.<br/>"
            f"Access the game here: <a href=\"{game_link}\">{game_link}</a><br/><br/>"
            "Enjoy!"
        ),
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
            player.email_status = EmailStatus.SENT
        else:
            logger.error(
                f"Failed to send email to {email}. Response Code: {response.status_code}, "
                f"Details: {response.text}"
            )
            player.email_status = EmailStatus.FAILED

    except RequestError as http_err:
        logger.error(f"HTTP request failed for {email}: {http_err}")
        player.email_status = EmailStatus.FAILED

    except Exception as general_err:
        logger.critical(f"Unexpected error for {email}: {general_err}")
        player.email_status = EmailStatus.FAILED

    finally:
        try:
            db.commit()
        except Exception as db_err:
            logger.critical(f"Failed to commit changes to the database: {db_err}")
            raise


# Batch Processing Function Example (Optional)
async def send_emails_in_batch(db: Session, players: list[ArenaSessionPlayers], email_data: list[dict]):
    """
    Processes and sends emails in batches to improve efficiency.

    Args:
        db (Session): Database session.
        players (list[ArenaSessionPlayers]): List of player records.
        email_data (list[dict]): List of email details (email, fullname, etc.).

    Returns:
        None
    """
    for player, data in zip(players, email_data):
        await send_invite_email(
            db=db,
            player=player,
            email=data["email"],
            fullname=data["fullname"],
            organisation_name=data["organisation_name"],
            game_name=data["game_name"],
            game_link=data["game_link"],
        )
    # Commit once after all emails are processed
    try:
        db.commit()
    except Exception as db_err:
        logger.critical(f"Failed to commit batch email updates: {db_err}")
        db.rollback()
