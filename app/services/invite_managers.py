from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from app.models import Group, GroupUsers  # Assuming these are your models
from app.payloads.request.GroupInviteManagerRequest import GroupManager
from app.services.organisation_service import get_organisation_service  # Assuming these are your services
from app.services.send_invite_manager import send_invite_manager
from app.services.user_service import get_user_service  # Assuming these are your services


async def invite_managers(
        db: Session,
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
    game_link = f"{organisation_name}.gamitool.com/group/{group.id}/invite"

    # Fetch all existing invited emails for the group
    existing_emails = get_existing_group_emails(db, group.id)

    # Process each manager
    for manager in managers:
        if should_skip_invitation(manager, existing_emails):
            continue

        # Fetch user details if available
        user_details = await fetch_user_details(manager)

        # Create or update the manager record
        manager_record = create_or_update_manager(db, group, manager, user_details)

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
        existing_emails.add(manager_record.user_email)

    db.commit()  # Persist changes to the database
    return {"message": "Emails queued for sending"}


def get_existing_group_emails(db: Session, group_id: str) -> set:
    """
    Fetches emails of already invited users for a group.

    Args:
        db (Session): The database session.
        group_id (int): The group ID.

    Returns:
        set: A set of emails of invited users.
    """
    return {
        user.user_email for user in db.query(GroupUsers).filter(GroupUsers.group_id == group_id).all() if
        user.user_email
    }


async def fetch_user_details(manager: GroupManager) -> Optional[object]:
    """
    Fetches user details either by user_id or email.

    Args:
        manager (GroupManager): The manager to fetch details for.

    Returns:
        Optional[object]: The user details or None if not found.
    """
    user_service = get_user_service()
    if manager.user_id:
        return await user_service.get_user_by_id(str(manager.user_id))
    if manager.user_email:
        return await user_service.get_user_by_email(manager.user_email)
    return None


def should_skip_invitation(manager: GroupManager, existing_emails: set) -> bool:
    """
    Checks if a manager should be skipped from invitation.

    Args:
        manager (GroupManager): The manager to check.
        existing_emails (set): A set of already invited emails.

    Returns:
        bool: True if the manager should be skipped, otherwise False.
    """
    return manager.user_email in existing_emails


def create_or_update_manager(
        db: Session,
        group: Group,
        manager: GroupManager,
        user_details: Optional[object]
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
