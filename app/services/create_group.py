from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.exceptions.critical_backend_error_exception import CriticalBackendErrorException
from app.payloads.request.GroupCreateRequest import GroupCreateRequest
from app.payloads.response.GroupCreateClientResponse import GroupCreateClientResponse
from app.services.invite_managers import invite_managers


# ---------------- Group CRUD Operations ----------------

async def create_group(db: AsyncSession, group_request: GroupCreateRequest, org_id: str, background_tasks):
    """
    Creates a new group and associates it with projects and managers.
    """
    try:
        db_group = await _create_group(db, group_request.name, org_id)
        await _associate_projects_with_group(db, db_group.id, group_request.project_ids)
        await invite_managers(db, db_group, group_request.managers, background_tasks)
        return GroupCreateClientResponse(
            id=db_group.id,
            name=db_group.name
        )
    except Exception as e:
        await db.rollback()  # Ensure to rollback in case of any error during the transaction
        raise CriticalBackendErrorException(f"Error creating group: {str(e)}") from e


async def _create_group(db: AsyncSession, group_name: str, org_id: str) -> models.Group:
    """
    Creates a group in the database.
    """
    db_group = models.Group(name=group_name, organisation_code=org_id)
    db.add(db_group)
    await db.commit()
    await db.refresh(db_group)
    return db_group


async def _associate_projects_with_group(db: AsyncSession, group_id: str, project_ids: list):
    """
    Associates a list of project IDs with a group.
    """
    project_group_mappings = [
        models.GroupProjects(group_id=group_id, project_id=project_id)
        for project_id in project_ids
    ]
    db.add_all(project_group_mappings)
    await db.commit()
