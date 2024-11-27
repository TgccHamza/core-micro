from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import Group, GroupArenas, GroupUsers, GroupProjects


async def delete_group(db: Session, group_id: str, org_id: str) -> bool:
    """
    Deletes a group from the system and removes its associations with arenas.

    Args:
        db (Session): The database session.
        group_id (str): The ID of the group to delete.
        org_id (str): The organization ID associated with the group.

    Returns:
        bool: True if the group was successfully deleted, False otherwise.

    Raises:
        ValueError: If the group or the organization does not exist.
        RuntimeError: If a database error occurs.
    """

    try:
        # Validate existence of the group
        group = db.query(Group).filter(Group.id == group_id, Group.organisation_code == org_id).first()
        if not group:
            raise ValueError(f"Group with ID {group_id} not found in organization {org_id}.")

        # Remove associations from GroupArenas table
        remove_associations_from_group(db, group_id)

        # Delete the group
        db.delete(group)
        db.commit()
        return True

    except SQLAlchemyError as e:
        db.rollback()  # Rollback transaction in case of an error
        raise RuntimeError("Database error occurred while deleting the group.") from e
    except ValueError as ve:
        raise ve
    except Exception as ex:
        raise RuntimeError("An unexpected error occurred while deleting the group.") from ex


def remove_associations_from_group(db: Session, group_id: str):
    """
    Removes all arena associations related to the group before deletion.

    Args:
        db (Session): The database session.
        group_id (str): The ID of the group to remove associations from.
    """

    try:
        # Find and delete all associations of this group in the GroupArenas table
        db.query(GroupUsers).filter(GroupUsers.group_id == group_id).delete(synchronize_session=False)
        db.query(GroupProjects).filter(GroupProjects.group_id == group_id).delete(
            synchronize_session=False)
        db.query(GroupArenas).filter(GroupArenas.group_id == group_id).delete(
            synchronize_session=False)
        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        raise RuntimeError(f"Error removing associations for group {group_id}.") from e


