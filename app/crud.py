from sqlalchemy.orm import Session
from uuid import uuid4

from . import models, schemas


# Generate a random slug (for simplicity)
def generate_slug(name: str):
    return name.lower().replace(" ", "-") + "-" + str(uuid4())[:8]


# Project CRUD Operations
def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(
        id=uuid4(),
        name=project.name,
        slug=generate_slug(project.name),
        client_id=project.client_id,
        client_name=project.client_name,
        visibility=project.visibility,
        domain=project.domain
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_project_by_id(db: Session, project_id: str):
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def get_project_by_slug(db: Session, slug: str):
    return db.query(models.Project).filter(models.Project.slug == slug).first()


def get_projects(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Project).offset(skip).limit(limit).all()


def update_project(db: Session, project_id: str, project_update: schemas.ProjectUpdate):
    db_project = get_project_by_id(db, project_id)
    if not db_project:
        return None
    for key, value in project_update.dict(exclude_unset=True).items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: str):
    db_project = get_project_by_id(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False


# ProjectModule CRUD Operations
def create_project_module(db: Session, module: schemas.ProjectModuleCreate, project_id: str):
    db_module = models.ProjectModule(
        id=uuid4(),
        name=module.name,
        type=module.type,
        db_index=module.db_index,
        project_id=project_id
    )
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module


def get_project_module_by_id(db: Session, module_id: str):
    return db.query(models.ProjectModule).filter(models.ProjectModule.id == module_id).first()


def get_modules_by_project_id(db: Session, project_id: str):
    return db.query(models.ProjectModule).filter(models.ProjectModule.project_id == project_id).all()


def update_project_module(db: Session, module_id: str, module_update: schemas.ProjectModuleUpdate):
    db_module = get_project_module_by_id(db, module_id)
    if not db_module:
        return None
    for key, value in module_update.dict(exclude_unset=True).items():
        setattr(db_module, key, value)
    db.commit()
    db.refresh(db_module)
    return db_module


def delete_project_module(db: Session, module_id: str):
    db_module = get_project_module_by_id(db, module_id)
    if db_module:
        db.delete(db_module)
        db.commit()
        return True
    return False
