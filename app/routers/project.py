from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from .. import models, schemas, crud
from ..database import get_db

router = APIRouter()

# Create a new project
@router.post("/projects", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = crud.get_project_by_slug(db, slug=project.slug)
    if db_project:
        raise HTTPException(status_code=400, detail="Project with this slug already exists")
    return crud.create_project(db=db, project=project)

# Get a project by ID
@router.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(project_id: UUID, db: Session = Depends(get_db)):
    db_project = crud.get_project_by_id(db, project_id=str(project_id))
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

# Get all projects
@router.get("/projects", response_model=list[schemas.Project])
def read_projects(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    projects = crud.get_projects(db, skip=skip, limit=limit)
    return projects

# Update a project
@router.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: UUID, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.update_project(db=db, project_id=project_id, project=project)

# Delete a project
@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: UUID, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    crud.delete_project(db=db, project_id=project_id)
    return {"detail": "Project deleted successfully"}

# Create a new project module
@router.post("/projects/{project_id}/modules/", response_model=schemas.ProjectModule, status_code=status.HTTP_201_CREATED)
def create_project_module(project_id: UUID, module: schemas.ProjectModuleCreate, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.create_project_module(db=db, module=module, project_id=project_id)

# Get all modules of a project
@router.get("/projects/{project_id}/modules/", response_model=list[schemas.ProjectModule])
def read_project_modules(project_id: UUID, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.get_project_modules(db=db, project_id=project_id)

# Update a project module
@router.put("/projects/{project_id}/modules/{module_id}", response_model=schemas.ProjectModule)
def update_project_module(project_id: UUID, module_id: UUID, module: schemas.ProjectModuleUpdate, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_module = crud.get_project_module(db=db, module_id=module_id)
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")

    return crud.update_project_module(db=db, module_id=module_id, module=module)

# Delete a project module
@router.delete("/projects/{project_id}/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_module(project_id: UUID, module_id: UUID, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_module = crud.get_project_module(db=db, module_id=module_id)
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")

    crud.delete_project_module(db=db, module_id=module_id)
    return {"detail": "Module deleted successfully"}
