from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from app.models import GroupArenas, Arena, Group


def validate_entity_exists(db: Session, model, entity_id: UUID, entity_name: str):
    """
    Validate that a given entity exists in the database.

    Args:
        db (Session): The database session.
        model: The ORM model of the entity.
        entity_id (UUID): The ID of the entity to validate.
        entity_name (str): The name of the entity for error messages.

    Raises:
        ValueError: If the entity does not exist.
    """

    if not db.query(model).filter(model.id == str(entity_id)).first():
        raise ValueError(f"{entity_name} with ID {entity_id} does not exist")


def create_group_arena_association(db: Session, arena_id: UUID, group_id: UUID) -> GroupArenas:
    """
    Create an association between an Arena and a Group.

    Args:
        db (Session): The database session.
        arena_id (UUID): The ID of the Arena to associate.
        group_id (UUID): The ID of the Group to associate with.

    Returns:
        GroupArenas: The created association object.

    Raises:
        IntegrityError: If the association already exists.
    """
    association = GroupArenas(group_id=str(group_id), arena_id=str(arena_id))
    db.add(association)
    try:
        db.commit()
        db.refresh(association)
    except IntegrityError as e:
        db.rollback()
        raise IntegrityError(f"Association between Arena {arena_id} and Group {group_id} already exists") from e
    return association


def associate_arena_with_group(db: Session, arena_id: UUID, group_id: UUID) -> dict:
    """
    Associate an Arena with an additional Group, with validation.

    Args:
        db (Session): The database session.
        arena_id (UUID): The ID of the Arena to associate.
        group_id (UUID): The ID of the Group to associate with.

    Returns:
        dict: Success message indicating the association.
    """
    # Validate that both the Arena and Group exist
    validate_entity_exists(db, Arena, arena_id, "Arena")
    validate_entity_exists(db, Group, group_id, "Group")

    try:
        create_group_arena_association(db, arena_id, group_id)
        return {"message": f"Arena {arena_id} successfully associated with Group {group_id}"}
    except IntegrityError as e:
        raise ValueError(f"Failed to associate: {e}")
