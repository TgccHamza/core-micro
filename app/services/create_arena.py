from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from app.models import Arena, GroupArenas, Group
from pydantic import BaseModel

from app.payloads.request.ArenaCreateRequest import ArenaCreateRequest
from app.services.organisation_service import get_organisation_service

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

async def create_arena(db: Session, arena: ArenaCreateRequest, org_id: str) -> Arena:
    """
    Create an arena for the given organization and associate it with a group.

    Args:
        db (Session): The database session.
        arena (ArenaCreateRequest): The data for the new arena.
        org_id (str): The organization ID to associate with the arena.

    Returns:
        Arena: The created arena object.
    """
    try:
        # Validate organization existence
        if not await check_organization_exists(org_id):
            raise ValueError(f"Organization with ID {org_id} does not exist.")

        # Create and persist the new arena
        db_arena = Arena(name=arena.name, organisation_code=org_id)
        db.add(db_arena)
        db.commit()
        db.refresh(db_arena)

        # Create association with the specified group
        await associate_group_with_arena(db, db_arena.id, arena.group_id)

        return db_arena

    except SQLAlchemyError as e:
        db.rollback()  # Rollback transaction in case of an error
        raise RuntimeError("Database error occurred while creating the arena.") from e
    except ValueError as ve:
        raise ve
    except Exception as ex:
        raise RuntimeError("An unexpected error occurred while creating the arena.") from ex


async def check_organization_exists(org_id: str) -> bool:
    """
    Check if the organization exists in the database.

    Args:
        db (Session): The database session.
        org_id (str): The organization ID to check.

    Returns:
        bool: True if the organization exists, False otherwise.
    """
    organization = get_organisation_service().get_organisation_name(organisation_code=org_id)
    return organization != "Unknown Organisation"


async def associate_group_with_arena(db: Session, arena_id: str, group_id: str):
    """
    Create an association between the arena and the specified group.

    Args:
        db (Session): The database session.
        arena_id (str): The ID of the arena to associate.
        group_id (str): The ID of the group to associate with the arena.
    """

    validate_entity_exists(db, Group, group_id, "Group")

    group_association = GroupArenas(group_id=group_id, arena_id=arena_id)
    db.add(group_association)
    db.commit()
