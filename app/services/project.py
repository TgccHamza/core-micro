from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app import models
from app.payloads.request.ModuleCreateRequest import ModuleCreateRequest
from app.payloads.request.ModuleUpdateRequest import ModuleUpdateRequest
from app.payloads.request.ProjectCreateRequest import ProjectCreateRequest
from app.payloads.request.ProjectUpdateRequest import ProjectUpdateRequest
from app.payloads.response.EspaceAdminClientResponse import EventGameResponse, FavoriteGameResponse, RecentGameResponse, \
    GroupResponse, ManagerResponse, ArenaResponse, AdminSpaceClientResponse


def list_projects(db: Session):
    """Retrieve a list of all projects."""
    return db.query(models.Project).all()


def list_modules(db: Session, project_id: str):
    """Retrieve a list of modules for a specific project."""
    return db.query(models.ProjectModule).filter(models.ProjectModule.project_id == project_id).all()


def create_project(db: Session, project: ProjectCreateRequest):
    db_project = models.Project(name=project.name,
                                description=project.description,
                                db_index=project.db_index,
                                slug=project.slug,
                                visibility=project.visibility,
                                game_type=project.game_type,
                                playing_type=project.playing_type,
                                activation_status=project.activation_status,
                                organisation_code=project.organisation_code,
                                client_id=project.client_id,
                                client_name=project.client_name,
                                start_time=project.start_time,
                                end_time=project.end_time,
                                tags=project.tags,
                                )
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


def update_project(db: Session, project_id: str, project: ProjectUpdateRequest):
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


def create_module(db: Session, module: ModuleCreateRequest):
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


def update_module(db: Session, module_id: str, module: ModuleUpdateRequest):
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


def favorite_project(db: Session, user_id: str, project_id: str):
    """Add a project to a user's favorites."""
    # Check if the project is already favorited
    existing_favorite = db.query(models.ProjectFavorite).filter_by(user_id=user_id, project_id=project_id).first()
    if existing_favorite:
        raise HTTPException(status_code=400, detail="Project is already in favorites")

    # Create a new favorite record
    favorite = models.ProjectFavorite(user_id=user_id, project_id=project_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


def unfavorite_project(db: Session, user_id: str, project_id: str):
    """Remove a project from a user's favorites."""
    favorite = db.query(models.ProjectFavorite).filter_by(user_id=user_id, project_id=project_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    db.delete(favorite)
    db.commit()
    return {"message": "Project removed from favorites"}


def list_favorites(db: Session, user_id: str):
    """Retrieve all favorite projects for a user."""
    favorites = db.query(models.Project).join(models.ProjectFavorite).filter(
        models.ProjectFavorite.user_id == user_id).all()
    return favorites


def espaceAdmin(db, user_id, org_id):
    # db.query(models.Project).filter().all()
    current_time = datetime.now()

    # Define the date range for projects starting within the next month
    one_month_later = current_time + timedelta(days=31)

    # Fetch all projects for the given user and organization that are starting within the next month
    projects = db.query(models.Project).filter(
        models.Project.organisation_code == org_id,
        models.Project.start_time >= current_time,
        models.Project.start_time <= one_month_later
    ).all()

    events = [EventGameResponse(
        id=project.id,
        game_name=project.name,
        client_name=project.client_name,
        visibility=project.visibility,
        online_date=project.start_time,
        game_type=project.game_type,
        playing_type=project.playing_type,
        total_players=(db.query(models.ArenaSessionPlayers).filter(
            models.ArenaSessionPlayers.module_id == project.module_game_id
        ).count()),
        tags=[x.strip() for x in project.tags.split(",")]
    ) for project in projects]

    favorite_projects = db.query(models.ProjectFavorite).filter(
        models.ProjectFavorite.user_id == user_id).all()  # Example query
    recent_projects = db.query(models.Project).filter(
        models.Project.organisation_code == org_id
    ).order_by(models.Project.created_at.desc()).limit(5).all()

    favorite_games = [
        FavoriteGameResponse(
            id=favorite_project.id,
            game_id=favorite_project.project.id,
            game_name=favorite_project.project.name,
            client_name=favorite_project.project.client_name,
            online_date=favorite_project.project.start_time
        ) for favorite_project in favorite_projects
    ]

    recent_games = [
        RecentGameResponse(
            id=project.id,
            game_name=project.name,
            client_name=project.client_name,
            visibility=project.visibility,
            online_date=project.start_time,
            game_type=project.game_type,
            playing_type=project.playing_type,
            total_players=(db.query(models.ArenaSessionPlayers).filter(
                models.ArenaSessionPlayers.module_id == project.module_game_id
            ).count()),
            groups=[
                GroupResponse(
                    id=group.id,
                    name=group.name,
                    managers=[ManagerResponse(
                        id=manager.user_id,
                        email=manager.user_email,
                        first_name=manager.first_name,
                        last_name=manager.last_name,
                        picture=manager.picture,
                    ) for manager in group.managers],
                    arenas=[ArenaResponse(
                        id=arena.id,
                        name=arena.name
                    ) for arena in group.arenas]
                ) for group in project.groups
            ]
        ) for project in recent_projects
    ]

    return AdminSpaceClientResponse(
        events=events,
        favorite_games=favorite_games,
        recent_games=recent_games
    )
