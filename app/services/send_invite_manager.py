import os
import re

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import GroupUsers  # Assuming these are your models
from app.enums import EmailStatus
from logging import getLogger

# Configure logger
logger = getLogger(__name__)


async def send_invite_manager(
        db: AsyncSession,
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

    if fullname is None:
        fullname = ""

    email_api_url = f"{os.getenv('URL_MAILER')}/api/v1/emails"
    # Get the path to the template file
    template_path = os.path.join('/app/app', "mails", "template_invite_manager.html")

    # Read the template
    with open(template_path, "r", encoding="utf-8") as file:
        template_content = file.read()

    # Replace placeholders with actual values
    template_content = template_content.replace("[Recipient Name]", fullname)
    template_content = template_content.replace("[OrgName]", organisation_name)
    template_content = template_content.replace("[Your CTA URL]", group_link.lower())
    template_content = re.sub(r"\s+", " ", template_content).strip()

    email_data = {
        "html_body": template_content,
        "is_html": True,
        "subject": f"{organisation_name} - Invitation to manage {group_name}",
        "to": email,
        "from": 'GAMITOOL'
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
            await db.commit()
            logger.info(f"Email status for {email} committed to the database.")
        except Exception as e:
            logger.exception(f"Failed to commit email status for {email}: {str(e)}")
