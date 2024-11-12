from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app import models, schemas


def list_projects(db: Session):
    """Retrieve a list of all projects."""
    return db.query(models.Project).all()

def list_modules(db: Session, project_id: str):
    """Retrieve a list of modules for a specific project."""
    return db.query(models.ProjectModule).filter(models.ProjectModule.project_id == project_id).all()

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(**project.dict())
    db.add(db_project)
    try:
        db.commit()
        db.refresh(db_project)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Slug or other unique field already exists.")
    return db_project

def get_project(db: Session, project_id: str):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

def update_project(db: Session, project_id: str, project: schemas.ProjectUpdate):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in project.dict(exclude_unset=True).items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: str):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}

def create_module(db: Session, module: schemas.ModuleCreate):
    db_module = models.ProjectModule(**module.dict())
    db.add(db_module)
    try:
        db.commit()
        db.refresh(db_module)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Unique constraint violation.")
    return db_module

def get_module(db: Session, module_id: str):
    module = db.query(models.ProjectModule).filter(models.ProjectModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module

def update_module(db: Session, module_id: str, module: schemas.ModuleUpdate):
    db_module = db.query(models.ProjectModule).filter(models.ProjectModule.id == module_id).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")
    for key, value in module.dict(exclude_unset=True).items():
        setattr(db_module, key, value)
    db.commit()
    db.refresh(db_module)
    return db_module

def delete_module(db: Session, module_id: str):
    db_module = db.query(models.ProjectModule).filter(models.ProjectModule.id == module_id).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")
    db.delete(db_module)
    db.commit()
    return {"message": "Module deleted successfully"}


def set_template_module(db: Session, module_id: str, template_code: str):
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