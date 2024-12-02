from typing import List, Optional, Sequence
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Group, GroupUsers  # Assuming these are your models
from app.payloads.request.GroupInviteManagerRequest import GroupManager
from app.payloads.response.UserResponse import UserResponse
from app.repositories.get_manager_email_by_group import get_manager_email_by_group
from app.services.organisation_service import get_organisation_service  # Assuming these are your services
from app.services.send_invite_manager import send_invite_manager
from app.services.user_service import get_user_service  # Assuming these are your services


async def invite_managers(
        db: AsyncSession,
        group: Group,
        managers: List[GroupManager],
        background_tasks: BackgroundTasks
):
    """
    Invites managers to a group by sending them invitation emails.
    Ensures that no duplicate invitations are sent.

    Args:
        db (Session): The database session.
        group (Group): The group to which managers are being invited.
        managers (List[GroupManager]): List of managers to invite.
        background_tasks (BackgroundTasks): Task queue for sending emails in the background.

    Returns:
        dict: A message indicating the status of email invitations.
    """

    # Prepare group and organisation details
    game_name = group.name
    organisation_name = await get_organisation_service().get_organisation_name(group.organisation_code)

    # Fetch all existing invited emails for the group
    existing_emails = await get_manager_email_by_group(group.id, db)
    existing_emails = list(existing_emails)
    if len(existing_emails) != 0:
        users = await get_user_service().get_users_by_email(existing_emails)
    else:
        users = {}

    # Process each manager
    for manager in managers:
        # if should_skip_invitation(manager, existing_emails):
        #     continue

        # Fetch user details if available
        user_details = users.get(manager.user_email, None)

        # Create or update the manager record
        manager_record = create_or_update_manager(db, group, manager, user_details)
        game_link = f"https://{organisation_name}.gamitool.com/group/{group.id}/invite?token={manager_record.id}"

        # Schedule email invitation
        background_tasks.add_task(
            send_invite_manager,
            db,
            manager_record,
            manager_record.user_email,
            f"{manager_record.first_name} {manager_record.last_name}",
            organisation_name,
            game_name,
            game_link,
        )

        # Mark email as processed
        existing_emails.append(manager_record.user_email)

    await db.commit()  # Persist changes to the database
    return {"message": "Emails queued for sending"}


def should_skip_invitation(manager: GroupManager, existing_emails: list[str]) -> bool:
    """
    Checks if a manager should be skipped from invitation.

    Args:
        manager (GroupManager): The manager to check.
        existing_emails (set): A set of already invited emails.

    Returns:
        bool: True if the manager should be skipped, otherwise False.
    """
    return existing_emails.__contains__(manager.user_email)


def create_or_update_manager(
        db: AsyncSession,
        group: Group,
        manager: GroupManager,
        user_details: Optional[UserResponse]
) -> GroupUsers:
    """
    Creates or updates a GroupUsers record for the manager.

    Args:
        db (Session): The database session.
        group (Group): The group to which the manager belongs.
        manager (GroupManager): The manager being added.
        user_details (Optional[object]): The user details.

    Returns:
        GroupUsers: The created or updated manager record.
    """
    manager_record = GroupUsers(
        group_id=group.id,
        user_email=user_details.user_email if user_details else manager.user_email,
        user_id=user_details.user_id if user_details else manager.user_id,
        first_name=user_details.first_name if user_details else manager.first_name,
        last_name=user_details.last_name if user_details else manager.last_name,
    )
    db.add(manager_record)
    return manager_record
