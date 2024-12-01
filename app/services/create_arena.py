from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Arena, GroupArenas, Group

from app.payloads.request.ArenaCreateRequest import ArenaCreateRequest
from app.repositories.get_group_by_id import get_group_by_id
from app.services.organisation_service import get_organisation_service

async def create_arena(db: AsyncSession, arena: ArenaCreateRequest, org_id: str) -> Arena:
    """
    Create an arena for the given organization and associate it with a group.

    Args:
        db (AsyncSession): The database AsyncSession.
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
        await db.commit()
        await db.refresh(db_arena)

        # Create association with the specified group
        await associate_group_with_arena(db, db_arena.id, str(arena.group_id))

        return db_arena

    except SQLAlchemyError as e:
        await db.rollback()  # Rollback transaction in case of an error
        raise RuntimeError("Database error occurred while creating the arena.") from e
    except ValueError as ve:
        raise ve
    except Exception as ex:
        raise RuntimeError("An unexpected error occurred while creating the arena.") from ex


async def check_organization_exists(org_id: str) -> bool:
    """
    Check if the organization exists in the database.

    Args:
        db (AsyncSession): The database AsyncSession.
        org_id (str): The organization ID to check.

    Returns:
        bool: True if the organization exists, False otherwise.
    """
    organization = get_organisation_service().get_organisation_name(organisation_code=org_id)
    return organization != "Unknown Organisation"


async def associate_group_with_arena(db: AsyncSession, arena_id: str, group_id: str):
    """
    Create an association between the arena and the specified group.

    Args:
        db (AsyncSession): The database AsyncSession.
        arena_id (str): The ID of the arena to associate.
        group_id (str): The ID of the group to associate with the arena.
    """
    group = await get_group_by_id(group_id, db)
    if group is None:
        raise ValueError(f"Group with ID {group_id} does not exist")

    group_association = GroupArenas(group_id=group_id, arena_id=arena_id)
    db.add(group_association)
    await db.commit()
