from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app import models
from app.payloads.request.ModuleCreateRequest import ModuleCreateRequest
from app.payloads.request.ModuleUpdateRequest import ModuleUpdateRequest
from app.payloads.request.ProjectUpdateRequest import ProjectUpdateRequest
from app.payloads.response.ProjectAdminResponse import ProjectAdminResponse
from app.repositories.get_all_projects import get_all_projects
from app.repositories.get_all_projects_by_org import get_all_projects_by_org
from app.services.organisation_service import get_organisation_service


async def list_projects(db: AsyncSession):
    organisation_service = get_organisation_service()
    projects = await get_all_projects(db)
    result = []
    for project in projects:
        organisation_name = await organisation_service.get_organisation_name(str(project.organisation_code))
        if organisation_name is None:
            organisation_name = "Unknown Organisation"

        result.append(ProjectAdminResponse(
            id=project.id,
            name=project.name,
            organisation_name=organisation_name,
            game_type=project.game_type,
            playing_type=project.playing_type,
            slug=project.slug,
            organisation_code=project.organisation_code
        ))

    return result


def list_modules(db: AsyncSession, project_id: str):
    """Retrieve a list of modules for a specific project."""
    return db.query(models.ProjectModule).filter(models.ProjectModule.project_id == project_id).all()


def update_project(db: AsyncSession, project_id: str, project: ProjectUpdateRequest):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in project.dict(exclude_unset=True).items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: AsyncSession, project_id: str):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}


def create_module(db: AsyncSession, module: ModuleCreateRequest):
    db_module = models.ProjectModule(**module.dict())
    db.add(db_module)
    try:
        db.commit()
        db.refresh(db_module)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Unique constraint violation.")
    return db_module


def get_module(db: AsyncSession, module_id: str):
    module = db.query(models.ProjectModule).filter(models.ProjectModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module


def update_module(db: AsyncSession, module_id: str, module: ModuleUpdateRequest):
    db_module = db.query(models.ProjectModule).filter(models.ProjectModule.id == module_id).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")
    for key, value in module.dict(exclude_unset=True).items():
        setattr(db_module, key, value)
    db.commit()
    db.refresh(db_module)
    return db_module


def delete_module(db: AsyncSession, module_id: str):
    db_module = db.query(models.ProjectModule).filter(models.ProjectModule.id == module_id).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")
    db.delete(db_module)
    db.commit()
    return {"message": "Module deleted successfully"}


def set_template_module(db: AsyncSession, module_id: str, template_code: str):
    """Set the template for a specific module."""
    # Retrieve the module
    module = db.query(models.ProjectModule).filter(models.ProjectModule.id == module_id).first()

    # Check if the module exists
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Set the template code
    module.template_code = template_code

    # Commit the changes
    db.commit()
    db.refresh(module)

    return {"message": "Template set successfully", "module_id": module_id, "template_code": template_code}


