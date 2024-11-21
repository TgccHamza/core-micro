from datetime import datetime, timedelta
from logging import Manager

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from starlette import status

from app import models
from app.models import ProjectComment
from app.payloads.request.GameUpdateRequest import GameUpdateRequest
from app.payloads.request.ModuleCreateRequest import ModuleCreateRequest
from app.payloads.request.ModuleUpdateRequest import ModuleUpdateRequest
from app.payloads.request.ProjectCommentCreateRequest import ProjectCommentCreateRequest
from app.payloads.request.ProjectCommentUpdateRequest import ProjectCommentUpdateRequest
from app.payloads.request.ProjectCreateRequest import ProjectCreateRequest
from app.payloads.request.ProjectUpdateRequest import ProjectUpdateRequest
from app.payloads.response.EspaceAdminClientResponse import EventGameResponse, FavoriteGameResponse, RecentGameResponse, \
    GroupResponse, ManagerResponse, ArenaResponse, AdminSpaceClientResponse
from app.payloads.response.GameViewClientResponse import GameViewArenaResponse, GameViewGroupResponse, \
    GameViewManagerResponse, GameViewSessionResponse, GameViewSessionPlayerClientResponse, GameViewClientResponse
from app.payloads.response.ProjectCommentResponse import ProjectCommentResponse


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
    favorites = (db.query(models.Project)
                 .join(models.ProjectFavorite, models.ProjectFavorite.project_id == models.Project.id)
                 .filter(models.ProjectFavorite.user_id == user_id).all())
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
    events = []
    project_ids = []
    for project in projects:
        project_ids.append(project.id)
        events.append(EventGameResponse(
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
        ))

    favorite_projects = db.query(models.ProjectFavorite).filter(
        models.ProjectFavorite.user_id == user_id).all()  # Example query
    favorite_games = []

    for favorite_project in favorite_projects:
        project_ids.append(favorite_project.project.id)
        favorite_games.append(
            FavoriteGameResponse(
                id=favorite_project.project.id,
                game_name=favorite_project.project.name,
                client_name=favorite_project.project.client_name,
                visibility=favorite_project.project.visibility,
                online_date=favorite_project.project.start_time,
                game_type=favorite_project.project.game_type,
                playing_type=favorite_project.project.playing_type,
                total_players=(db.query(models.ArenaSessionPlayers).filter(
                    models.ArenaSessionPlayers.module_id == favorite_project.project.module_game_id
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
                    ) for group in favorite_project.project.groups
                ]
            ))

    recent_projects = db.query(models.Project).filter(
        models.Project.organisation_code == org_id
    ).order_by(models.Project.created_at.desc()).limit(5).all()

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


def gameView(db, org_id, game_id):
    game = db.query(models.Project).filter(
        models.Project.organisation_code == org_id,
        models.Project.id == game_id
    ).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    total_groups = (db.query(models.GroupProjects)
                    .filter(models.GroupProjects.project_id == game.id).count())

    total_managers = (db.query(models.Group)
                      .join(models.GroupProjects, models.Group.id == models.GroupProjects.group_id)
                      .join(models.GroupUsers, models.Group.id == models.GroupUsers.group_id)
                      .filter(models.GroupProjects.project_id == game_id)
                      .count())

    sessions = game.arena_sessions
    arena_items = (db.query(models.Arena)
                   .join(models.GroupArenas, models.Arena.id == models.GroupArenas.arena_id)
                   .join(models.GroupProjects, models.GroupArenas.group_id == models.GroupProjects.group_id)
                   .filter(models.GroupProjects.project_id == game_id)
                   .all())

    arenas = {}

    for arena in arena_items:
        arena_resp = GameViewArenaResponse(id=arena.id, name=arena.name, sessions=[])
        if len(arena.groups) > 0:
            arena_resp.group = GameViewGroupResponse(
                id=arena.groups[0].id,
                name=arena.groups[0].name,
                managers=[
                    GameViewManagerResponse(id=manager.user_id, email=manager.user_email,
                                            first_name=manager.first_name, last_name=manager.last_name,
                                            picture=manager.picture)
                    for manager in arena.groups[0].managers
                ]
            )
        arenas[arena.id] = arena_resp

    for session in sessions:
        gameview_session = GameViewSessionResponse(id=session.id,
                                                   period_type=session.period_type,
                                                   start_time=session.start_time,
                                                   end_time=session.end_time,
                                                   access_status=session.access_status,
                                                   session_status=session.session_status,
                                                   view_access=session.view_access,
                                                   players=[
                                                       GameViewSessionPlayerClientResponse(
                                                           user_id=player.user_id,
                                                           email=player.user_email,
                                                           first_name=None,
                                                           last_name=None,
                                                           picture=None
                                                       )
                                                       for player in session.players
                                                   ]
                                                   )
        if session.arena.id in arenas:
            arenas[session.arena.id].sessions.append(gameview_session)

    return GameViewClientResponse(
        id=game.id,
        game_name=game.name,
        client_name=game.client_name,
        description=game.description,
        visibility=game.visibility,
        online_date=game.start_time,
        end_date=game.end_time,
        game_type=game.game_type,
        playing_type=game.playing_type,
        total_managers=total_managers,
        total_groups=total_groups,
        arenas=[arenas[key] for key in arenas],
        total_players=(db.query(models.ArenaSessionPlayers).filter(
            models.ArenaSessionPlayers.module_id == game.module_game_id
        ).count()),
        tags=[x.strip() for x in game.tags.split(",")]
    )


def config_client_game(db, org_id, project_id):
    project = db.query(models.Project).filter(models.Project.organisation_code == org_id,
                                              models.Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project


def update_client_game(db: Session, org_id: str, project_id: str, update_data: GameUpdateRequest):
    # Fetch the project by ID
    project = db.query(models.Project).filter(models.Project.organisation_code == org_id,
                                              models.Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Update fields if they are provided in the update_data
    if update_data.name is not None:
        project.name = update_data.name
    if update_data.description is not None:
        project.description = update_data.description
    if update_data.game_trailer_url is not None:
        project.game_trailer_url = update_data.game_trailer_url
    if update_data.visibility is not None:
        project.visibility = update_data.visibility
    if update_data.activation_status is not None:
        project.activation_status = update_data.activation_status
    if update_data.client_name is not None:
        project.client_name = update_data.client_name
    if update_data.tags is not None:
        project.tags = update_data.tags
    if update_data.allow_comments is not None:
        project.allow_comments = update_data.allow_comments
    if update_data.replayable is not None:
        project.replayable = update_data.replayable
    if update_data.public_leaderboard is not None:
        project.public_leaderboard = update_data.public_leaderboard
    if update_data.timezone is not None:
        project.timezone = update_data.timezone
    if update_data.restrict_playing_hours is not None:
        project.restrict_playing_hours = update_data.restrict_playing_hours
    if update_data.playing_start_time is not None:
        project.playing_start_time = update_data.playing_start_time
    if update_data.playing_end_time is not None:
        project.playing_end_time = update_data.playing_end_time

    # Commit changes to the database
    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def create_comment(db: Session, project_id: str, user_id: str, comment_text: str) -> ProjectCommentResponse:
    """
    Create a new project comment.
    """
    new_comment = ProjectComment(project_id=project_id, user_id=user_id, comment_text=comment_text)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


def get_comment(db: Session, comment_id: str) -> ProjectCommentResponse:
    """
    Retrieve a single comment by ID.
    """
    comment = db.query(ProjectComment).filter(ProjectComment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    return comment


def list_comments(
        db: Session,
        project_id: str = None
) -> list[ProjectCommentResponse]:
    """
    List comments based on filters.
    """
    query = db.query(ProjectComment)
    query = query.filter(ProjectComment.project_id == project_id)
    query = query.filter(ProjectComment.visible == True)
    return query.all()


def update_comment(
        db: Session, comment_id: str, updated_data: ProjectCommentUpdateRequest, user_id
) -> ProjectComment:
    """
    Update an existing comment.
    """
    comment = db.query(ProjectComment).filter(ProjectComment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    if comment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not allowed to edit this comment",
        )

    comment.comment_text = updated_data.comment_text

    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment_id: str, user_id: str):
    """
    Delete a comment by ID.
    """
    comment = db.query(ProjectComment).filter(ProjectComment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    if comment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not the owner of the comment to deleted",
        )

    db.delete(comment)
    db.commit()
    return {"detail": "Comment deleted"}
