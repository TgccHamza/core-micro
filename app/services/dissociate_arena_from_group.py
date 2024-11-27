from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from uuid import UUID
from app.models import GroupArenas


def get_group_arena_association(db: Session, arena_id: UUID, group_id: UUID) -> GroupArenas:
    """
    Retrieve the association between an Arena and a Group.

    Args:
        db (Session): The database session.
        arena_id (UUID): The ID of the Arena.
        group_id (UUID): The ID of the Group.

    Returns:
        GroupArenas: The association object if found.

    Raises:
        NoResultFound: If the association does not exist.
    """
    association = (
        db.query(GroupArenas)
        .filter(
            GroupArenas.arena_id == str(arena_id),
            GroupArenas.group_id == str(group_id)
        )
        .first()
    )
    if not association:
        raise NoResultFound(f"No association found between Arena {arena_id} and Group {group_id}")
    return association


def dissociate_arena_from_group(db: Session, arena_id: UUID, group_id: UUID) -> dict:
    """
    Dissociate an Arena from a specific Group.

    Args:
        db (Session): The database session.
        arena_id (UUID): The ID of the Arena to dissociate.
        group_id (UUID): The ID of the Group to dissociate from.

    Returns:
        dict: Success message indicating the dissociation.
    """
    try:
        association = get_group_arena_association(db, arena_id, group_id)
        db.delete(association)
        db.commit()
        return {"message": f"Arena {arena_id} successfully dissociated from Group {group_id}"}
    except NoResultFound as e:
        raise NoResultFound(f"Failed to dissociate: {e}")
