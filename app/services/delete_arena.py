from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from app.models import Arena, GroupArenas


def get_arena_by_id(db: Session, arena_id: UUID, org_id: str) -> Arena:
    """
    Retrieve an Arena by its ID and organization code.

    Args:
        db (Session): The database session.
        arena_id (UUID): The ID of the Arena to retrieve.
        org_id (str): The organization code to validate.

    Returns:
        Arena: The Arena object if found.

    Raises:
        ValueError: If the Arena is not found.
    """
    arena = db.query(Arena).filter(Arena.id == str(arena_id), Arena.organisation_code == org_id).first()
    if not arena:
        raise ValueError(f"Arena with ID {arena_id} not found in organization {org_id}")
    return arena


def delete_arena_associations(db: Session, arena_id: UUID):
    """
    Delete all associations of an Arena with groups.

    Args:
        db (Session): The database session.
        arena_id (UUID): The ID of the Arena whose associations should be deleted.
    """
    db.query(GroupArenas).filter(GroupArenas.arena_id == str(arena_id)).delete()


def delete_arena(db: Session, arena_id: UUID, org_id: str) -> dict:
    """
    Delete an Arena and its associated group links.

    Args:
        db (Session): The database session.
        arena_id (UUID): The ID of the Arena to delete.
        org_id (str): The organization code to validate.

    Returns:
        dict: Success message if the deletion is successful.

    Raises:
        ValueError: If the Arena is not found.
        SQLAlchemyError: If any database error occurs during the operation.
    """
    try:
        # Retrieve the Arena
        arena = get_arena_by_id(db, arena_id, org_id)

        # Delete associated records
        delete_arena_associations(db, arena_id)

        # Delete the Arena itself
        db.delete(arena)
        db.commit()
        return {"message": f"Arena {arena_id} deleted successfully"}
    except ValueError as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise RuntimeError(f"Database error occurred while deleting Arena {arena_id}: {e}")
