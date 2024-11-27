import httpx
from sqlalchemy.orm import Session
from app.models import GroupUsers  # Assuming these are your models
from app.enums import  EmailStatus
from logging import getLogger

# Configure logger
logger = getLogger(__name__)


async def send_invite_manager(
    db: Session,
    manager: GroupUsers,
    email: str,
    fullname: str,
    organisation_name: str,
    group_name: str,
    group_link: str
):
    """
    Sends an invitation email to the manager and updates email status.

    Args:
        db (Session): The database session.
        manager (GroupUsers): The manager record to update.
        email (str): The email address of the manager.
        fullname (str): The full name of the manager.
        organisation_name (str): Name of the organisation.
        group_name (str): Name of the group.
        group_link (str): Link to the group invitation.

    Returns:
        None
    """
    email_api_url = "https://dev-api.thegamechangercompany.io/mailer/api/v1/emails"
    email_data = {
        "html_body": (
            f"Hi {fullname},<br><br>"
            f"Welcome to the Gaming Tool platform!<br>"
            f"You have been invited by {organisation_name} to manage the group: "
            f"<a href=\"{group_link}\">{group_name}</a>."
        ),
        "is_html": True,
        "subject": f"{organisation_name} - Invitation to manage {group_name}",
        "to": email,
    }

    try:
        # Send the email asynchronously
        async with httpx.AsyncClient() as client:
            response = await client.post(email_api_url, json=email_data)

        # Handle response
        if response.status_code in {200, 201, 202}:
            logger.info(f"Email sent successfully to {email}")
            manager.email_status = EmailStatus.SENT
        else:
            logger.error(
                f"Failed to send email to {email}. Status: {response.status_code}, Response: {response.text}"
            )
            manager.email_status = EmailStatus.FAILED

    except httpx.RequestError as e:
        logger.error(f"Request error while sending email to {email}: {str(e)}")
        manager.email_status = EmailStatus.FAILED

    except Exception as e:
        logger.exception(f"Unexpected error while sending email to {email}: {str(e)}")
        manager.email_status = EmailStatus.FAILED

    finally:
        # Ensure the email status is committed to the database
        try:
            db.commit()
            logger.info(f"Email status for {email} committed to the database.")
        except Exception as e:
            logger.exception(f"Failed to commit email status for {email}: {str(e)}")
