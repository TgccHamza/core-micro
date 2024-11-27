from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from app.models import Arena
from app.payloads.request import ArenaUpdateRequest


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

def update_arena(db: Session, arena_id: UUID, arena_request: ArenaUpdateRequest, org_id: str) -> Arena:
    """
    Update an Arena's details.

    Args:
        db (Session): The database session.
        arena_id (UUID): The ID of the Arena to update.
        arena_request (ArenaUpdateRequest): The updated details for the Arena.
        org_id (str): The organization code for validation.

    Returns:
        Arena: The updated Arena object.

    Raises:
        ValueError: If the Arena is not found or if the update request is invalid.
        RuntimeError: If any database error occurs during the operation.
    """
    try:

        # Retrieve the Arena
        arena = get_arena_by_id(db, arena_id, org_id)

        # Update fields conditionally
        if arena_request.name is not None:
            arena.name = arena_request.name

        # Commit the changes
        db.commit()
        db.refresh(arena)
        return arena
    except ValueError as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise RuntimeError(f"Database error occurred while updating Arena {arena_id}: {e}")
