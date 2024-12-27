from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.not_found_exception import NotFoundException
from app.exceptions.validation_error_exception import ValidationErrorException
from app.models import Arena, GroupArenas, Group

from app.payloads.request.ArenaCreateRequest import ArenaCreateRequest
from app.payloads.response.ArenaCreateResponse import ArenaCreateResponse
from app.repositories.get_group_by_id import get_group_by_id
from app.services.organisation_service import get_organisation_service

async def create_arena(db: AsyncSession, arena: ArenaCreateRequest, org_id: str) -> ArenaCreateResponse:
    """
    Asynchronously creates a new arena and associates it with a specified group.
    Args:
        db (AsyncSession): The database session to use for the operation.
        arena (ArenaCreateRequest): The request object containing the details of the arena to be created.
        org_id (str): The ID of the organization to which the arena belongs.
    Returns:
        ArenaCreateResponse: The response object containing the details of the created arena.
    Raises:
        ValidationErrorException: If the organization with the specified ID does not exist.
        Exception: If any other error occurs during the operation.
    """
    try:
        # Validate organization existence
        if not await check_organization_exists(org_id):
            raise ValidationErrorException(f"Organization with ID {org_id} does not exist.")

        # Create and persist the new arena
        db_arena = Arena(name=arena.name, organisation_code=org_id)
        db.add(db_arena)
        await db.commit()
        await db.refresh(db_arena)

        # Create association with the specified group
        await associate_group_with_arena(db, db_arena.id, str(arena.group_id))

        return ArenaCreateResponse(id=db_arena.id, name=db_arena.name)
    except Exception as ex:
        await db.rollback()  # Rollback transaction in case of an error
        raise ex


async def check_organization_exists(org_id: str) -> bool:
    """
    Check if an organization exists based on the given organization ID.

    Args:
        org_id (str): The ID of the organization to check.

    Returns:
        bool: True if the organization exists, False otherwise.
    """
    organization = get_organisation_service().get_organisation_name(organisation_code=org_id)
    return organization != "Unknown Organisation"


async def associate_group_with_arena(db: AsyncSession, arena_id: str, group_id: str):
    """
    Associates a group with an arena by creating a new GroupArenas record in the database.
    Args:
        db (AsyncSession): The database session to use for the operation.
        arena_id (str): The ID of the arena to associate the group with.
        group_id (str): The ID of the group to be associated with the arena.
    Raises:
        NotFoundException: If the group with the specified ID does not exist.
    Returns:
        None
    """
    group = await get_group_by_id(group_id, db)
    if group is None:
        raise NotFoundException(error=f"Group with ID {group_id} does not exist")

    group_association = GroupArenas(group_id=group_id, arena_id=arena_id)
    db.add(group_association)
    await db.commit()
