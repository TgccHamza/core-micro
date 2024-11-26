from typing import List

import httpx
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from app import models
from uuid import UUID
from sqlalchemy.exc import NoResultFound

from app.enums import EmailStatus, SessionStatus, ActivationStatus, AccessStatus, ViewAccess
from app.models import ArenaSession, Project, ArenaSessionPlayers, Arena, Group, GroupUsers
from app.payloads.request.ArenaCreateRequest import ArenaCreateRequest
from app.payloads.request.ArenaUpdateRequest import ArenaUpdateRequest
from app.payloads.request.GroupCreateRequest import GroupCreateRequest, GroupManager
from app.payloads.request.GroupUpdateRequest import GroupUpdateRequest
from app.payloads.request.InvitePlayerRequest import InvitePlayerRequest
from app.payloads.request.SessionConfigRequest import SessionConfigRequest
from app.payloads.request.SessionCreateRequest import SessionCreateRequest
from app.payloads.request.SessionUpdateRequest import SessionUpdateRequest
from app.payloads.response.ArenaListResponseTop import ArenaListResponseTop, ArenaMembers, ArenaListGroupClientResponse, \
    ArenaListGroupUserClientResponse
from app.payloads.response.GroupByGameResponse import GroupByGameResponse, GroupByGameArenaClientResponse, \
    GroupByGameArenaSessionResponse, GroupByGameSessionPlayerClientResponse, GroupByGameUserClientResponse


# ---------------- Group CRUD Operations ----------------

def create_group(db: Session, group: GroupCreateRequest, org_id: str, background_tasks):
    db_group = models.Group(name=group.name, organisation_code=org_id)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)

    for project_id in group.project_ids:
        db_project_group = models.GroupProjects(group_id=db_group.id, project_id=project_id)
        db.add(db_project_group)
    db.commit()

    invite_managers(db, db_group, group.managers, background_tasks)

    return db_group


def get_groups(db: Session, org_id: str):
    return db.query(models.Group).filter(models.Group.organisation_code == org_id).all()


def get_group(db: Session, group_id: str, org_id: str):
    return db.query(models.Group).filter(models.Group.id == group_id, models.Group.organisation_code == org_id).first()


def update_group(db: Session, group_id: str, group: GroupUpdateRequest, org_id: str):
    db_group = get_group(db, group_id, org_id)
    if not db_group:
        raise NoResultFound("Group not found")

    db_group.name = group.name

    # Update Projects
    db.query(models.GroupProjects).filter(models.GroupProjects.group_id == group_id).delete()
    for project_id in group.project_ids:
        db_project_group = models.GroupProjects(group_id=group_id, project_id=project_id)
        db.add(db_project_group)

    db.commit()
    return db_group


def delete_group(db: Session, group_id: str, org_id: str):
    db_group = get_group(db, group_id, org_id)
    if not db_group:
        raise NoResultFound("Group not found")

    db.query(models.GroupUsers).filter(models.GroupUsers.group_id == group_id).delete()
    db.query(models.GroupProjects).filter(models.GroupProjects.group_id == group_id).delete()
    db.delete(db_group)
    db.commit()
    return {"message": "Group deleted successfully"}


# ---------------- Arena CRUD Operations ----------------

# Create an Arena and associate it with a single group
def create_arena(db: Session, arena: ArenaCreateRequest, org_id: str):
    db_arena = models.Arena(name=arena.name, organisation_code=org_id)
    db.add(db_arena)
    db.commit()
    db.refresh(db_arena)

    # Associate the arena with the specified group
    group_association = models.GroupArenas(group_id=str(arena.group_id), arena_id=db_arena.id)
    db.add(group_association)
    db.commit()
    return db_arena


# Get all Arenas with their associated groups
def get_arenas(db: Session, org_id: str):
    arenas_data = db.query(models.Arena).filter(models.Arena.organisation_code == org_id).all()
    arenas = []
    for db_arena in arenas_data:
        arena = ArenaListResponseTop(id=db_arena.id,
                                     name=db_arena.name,
                                     groups=[],
                                     players=[])
        groups = []
        for db_group in db_arena.groups:
            group = ArenaListGroupClientResponse(
                id=db_group.id,
                name=db_group.name,
                managers=[ArenaListGroupUserClientResponse(
                    user_id=manager.user_id,
                    user_email=manager.user_email,
                    user_name=f"{manager.first_name} {manager.last_name}",
                    picture=manager.picture
                ) for manager in db_group.managers]
            )
            groups.append(group)
        arena.groups = groups
        dict_players = set()
        players = []
        for session in db_arena.sessions:
            for player in session.players:
                if player.user_email not in dict_players:
                    dict_players.add(player.user_email)
                    players.append(ArenaMembers(
                        user_id=player.user_id,
                        user_email=player.user_email,
                        user_name=player.user_name,
                        picture=None
                    ))
        arena.players = players
        arenas.append(arena)
    return arenas


# Get a specific Arena by ID
def get_arena(db: Session, arena_id: UUID, org_id: str):
    return db.query(models.Arena).filter(models.Arena.id == str(arena_id),
                                         models.Arena.organisation_code == org_id).first()


def show_arena(db: Session, arena_id: UUID, org_id: str):
    db_arena = get_arena(db, arena_id, org_id)

    if not db_arena:
        raise NoResultFound("Arena not found")

    arena = ArenaListResponseTop(id=db_arena.id,
                                 name=db_arena.name,
                                 groups=[],
                                 players=[])
    groups = []
    for db_group in db_arena.groups:
        group = ArenaListGroupClientResponse(
            id=db_group.id,
            name=db_group.name,
            managers=[ArenaListGroupUserClientResponse(
                user_id=manager.user_id,
                user_email=manager.user_email,
                user_name=f"{manager.first_name} {manager.last_name}",
                picture=manager.picture
            ) for manager in db_group.managers]
        )
        groups.append(group)
    arena.groups = groups
    dict_players = set()
    players = []
    for session in db_arena.sessions:
        for player in session.players:
            if player.user_email not in dict_players:
                dict_players.add(player.user_email)
                players.append(ArenaMembers(
                    user_id=player.user_id,
                    user_email=player.user_email,
                    user_name=player.user_name,
                    picture=None
                ))
    arena.players = players
    return arena


# Update Arena name only (group association updates are not allowed here)
def update_arena(db: Session, arena_id: UUID, arena: ArenaUpdateRequest, org_id: str):
    db_arena = get_arena(db, arena_id, org_id)
    if not db_arena:
        raise NoResultFound("Arena not found")

    if arena.name is not None:
        db_arena.name = arena.name

    db.commit()
    return db_arena


# Delete an Arena
def delete_arena(db: Session, arena_id: UUID, org_id: str):
    db_arena = get_arena(db, arena_id, org_id)
    if not db_arena:
        raise NoResultFound("Arena not found")

    db.query(models.GroupArenas).filter(models.GroupArenas.arena_id == str(arena_id)).delete()
    db.delete(db_arena)
    db.commit()
    return {"message": "Arena deleted successfully"}


# Associate an Arena with an additional group
def associate_arena_with_group(db: Session, arena_id: UUID, group_id: UUID):
    association = models.GroupArenas(group_id=str(group_id), arena_id=str(arena_id))
    db.add(association)
    db.commit()
    return {"message": f"Arena {arena_id} associated with Group {group_id}"}


# Dissociate an Arena from a specific group
def dissociate_arena_from_group(db: Session, arena_id: UUID, group_id: UUID):
    association = db.query(models.GroupArenas).filter(
        models.GroupArenas.arena_id == str(arena_id),
        models.GroupArenas.group_id == str(group_id)
    ).first()

    if association:
        db.delete(association)
        db.commit()
        return {"message": f"Arena {arena_id} dissociated from Group {group_id}"}
    else:
        raise NoResultFound("Association not found")


# ---------------- Session CRUD Operations ----------------

def create_session(db: Session, session: SessionCreateRequest, org_id: str):
    project = (db.query(Project)
               .filter(Project.organisation_code == org_id, Project.id == str(session.game_id)).first())
    if not project:
        raise NoResultFound("Project not found")

    arena = db.query(Arena).filter(Arena.organisation_code == org_id, Arena.id == str(session.arena_id)).first()
    if not arena:
        raise NoResultFound("Arena not found")

    db_session = models.ArenaSession(
        arena_id=str(session.arena_id),
        project_id=str(session.game_id),
        session_status=SessionStatus.PENDING,
        activation_status=ActivationStatus.INACTIVE,
        access_status=AccessStatus.AUTH,
        view_access=ViewAccess.SESSION,
        organisation_code=org_id,
        player_module_id=str(project.module_game_id),
        gamemaster_module_id=str(project.module_gamemaster_id),
        super_game_master_module_id=str(project.module_super_game_master_id)
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_sessions(db: Session, org_id: str):
    return db.query(models.ArenaSession).filter(models.ArenaSession.organisation_code == org_id).all()


def get_session(db: Session, session_id: str, org_id: str):
    return db.query(models.ArenaSession).filter(models.ArenaSession.id == session_id,
                                                models.ArenaSession.organisation_code == org_id).first()


def update_session(db: Session, session_id: str, session: SessionUpdateRequest, org_id: str):
    db_session = get_session(db, session_id, org_id=org_id)
    if not db_session:
        raise NoResultFound("Session not found")

    db_session.period_type = session.period_type
    db_session.start_time = session.start_time
    db_session.end_time = session.end_time
    db_session.access_status = session.access_status
    db_session.session_status = session.session_status
    db_session.view_access = session.view_access
    db_session.project_id = session.project_id

    # Update Players
    db.query(models.ArenaSessionPlayers).filter(models.ArenaSessionPlayers.session_id == session_id).delete()
    for user_id in session.user_ids:
        db_player = models.ArenaSessionPlayers(session_id=session_id, user_id=user_id)
        db.add(db_player)

    db.commit()
    return db_session


def config_session(db: Session, session_id: str, session: SessionConfigRequest, org_id: str):
    db_session = get_session(db, session_id, org_id=org_id)
    if not db_session:
        raise NoResultFound("Session not found")

    db_session.period_type = session.period_type
    db_session.start_time = session.start_time
    db_session.end_time = session.end_time
    db_session.access_status = session.access_status
    db_session.session_status = session.session_status
    db_session.view_access = session.view_access
    db.commit()
    return db_session


def delete_session(db: Session, session_id: str, org_id: str):
    db_session = get_session(db, session_id, org_id)
    if not db_session:
        raise NoResultFound("Session not found")

    db.query(models.ArenaSessionPlayers).filter(models.ArenaSessionPlayers.session_id == session_id).delete()
    db.delete(db_session)
    db.commit()
    return {"message": "Session deleted successfully"}


# Update send_invite_email function to handle email status
async def send_invite_email(db: Session, player: ArenaSessionPlayers, email: str, fullname: str, organisation_name,
                            game_name, game_link):
    url = "https://dev-api.thegamechangercompany.io/mailer/api/v1/emails"
    try:
        async with httpx.AsyncClient() as client:
            email_data = {
                "html_body": f"Hi {fullname}, Welcome to gaming tool platform you have been invited from {organisation_name} to play this game link: <br/> <a href=\"{game_link}\">{game_name}</a>",
                "is_html": True,
                "subject": f"{organisation_name}  Invitation link to play {game_name}",
                "to": email
            }
            response = await client.post(url, json=email_data)

            if response.status_code == 200 or response.status_code == 202 or response.status_code == 201:
                print(f"Email sent successfully to {email_data['to']}")
                player.email_status = EmailStatus.SENT  # Update status to SENT
            else:
                print(f"Failed to send email: {response.status_code}, {response.text}")
                player.email_status = EmailStatus.FAILED  # Update status to FAILED

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        player.email_status = EmailStatus.FAILED  # Update status to FAILED on error

    db.commit()  # Commit the email status update in the database


# Update send_invite_email function to handle email status
async def send_invite_manager(db: Session, manager: GroupUsers, email: str, fullname: str, organisation_name,
                              group_name, group_link):
    url = "https://dev-api.thegamechangercompany.io/mailer/api/v1/emails"
    try:
        async with httpx.AsyncClient() as client:
            email_data = {
                "html_body": f"Hi {fullname}, Welcome to gaming tool platform you have been invited from {organisation_name} to manage this group link: <a href=\"{group_link}\">{group_name}</a>",
                "is_html": True,
                "subject": f"{organisation_name}  Invitation link to manage {group_name}",
                "to": email
            }
            response = await client.post(url, json=email_data)

            if response.status_code == 200 or response.status_code == 202 or response.status_code == 201:
                print(f"Email sent successfully to {email_data['to']}")
                manager.email_status = EmailStatus.SENT  # Update status to SENT
            else:
                print(f"Failed to send email: {response.status_code}, {response.text}")
                manager.email_status = EmailStatus.FAILED  # Update status to FAILED

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        manager.email_status = EmailStatus.FAILED  # Update status to FAILED on error

    db.commit()  # Commit the email status update in the database


# Updated invite_players function to integrate email status
async def invite_players(
        db: Session,
        session: ArenaSession,
        invite_req: InvitePlayerRequest,
        background_tasks: BackgroundTasks
):
    project = db.query(Project).filter(Project.id == session.project_id).first()
    if not project:
        raise ValueError("Project not found for the session")

    # Get the game and organization info
    game_name = project.name
    game_link = f"{project.organisation_code}.gamitool.com/{project.slug}/invite"
    organisation_name = f"{project.organisation_code}"  # Example: you could fetch this dynamically

    # Send invitation emails in the background
    for user in invite_req.members:
        if user.user_email:
            db_player = ArenaSessionPlayers(
                session_id=session.id,
                user_name=str(user.user_fullname),
                user_email=str(user.user_email),
                user_id=str(user.user_id),
                organisation_code=session.organisation_code,
                email_status=EmailStatus.PENDING  # Set initial email status to PENDING
            )
            db.add(db_player)

            # Add the email sending task with updated status tracking
            background_tasks.add_task(
                send_invite_email, db, db_player, user.user_email, user.user_fullname, organisation_name, game_name,
                game_link
            )

    db.commit()  # Commit the new players to the database
    return {"message": "Emails queued for sending"}


# Updated invite_players function to integrate email status
def invite_managers(db: Session, group: Group, managers: List[GroupManager], background_tasks: BackgroundTasks):
    # Get the game and organization info
    game_name = group.name
    game_link = f"{group.organisation_code}.gamitool.com/group/{group.id}/invite"
    organisation_name = f"{group.organisation_code}"  # Example: you could fetch this dynamically

    # Send invitation emails in the background
    for user in managers:
        if user.user_email:
            manager = GroupUsers(
                group_id=group.id,
                user_email=str(user.user_email),
                user_id=str(user.user_id)
            )
            db.add(manager)

            # Add the email sending task with updated status tracking
            background_tasks.add_task(
                send_invite_manager, db, manager, user.user_email, f"{user.first_name} {user.last_name}",
                organisation_name, game_name, game_link)

    db.commit()  # Commit the new players to the database
    return {"message": "Emails queued for sending"}


def groups_by_game(db: Session, game: Project):
    groups = []
    for db_group in game.groups:
        group = GroupByGameResponse(
            id=db_group.id,
            name=db_group.name,
            managers=[],
            arenas=[]
        )
        for db_arena in db_group.arenas:
            arena = GroupByGameArenaClientResponse(
                id=db_arena.id,
                name=db_arena.name,
                sessions=[]
            )
            arena_sessions = db.query(ArenaSession).filter(
                ArenaSession.project_id == game.id,
                ArenaSession.arena_id == arena.id
            )
            for db_session in arena_sessions:
                session = GroupByGameArenaSessionResponse(
                    id=db_session.id,
                    period_type=db_session.period_type,
                    start_time=db_session.start_time,
                    end_time=db_session.end_time,
                    access_status=db_session.access_status,
                    session_status=db_session.session_status,
                    view_access=db_session.view_access,
                    players=[]
                )
                for db_player in session.players:
                    player = GroupByGameSessionPlayerClientResponse(
                        user_id=db_player.user_id,
                        email=db_player.user_email,
                        first_name=db_player.user_name,
                        last_name=db_player.user_name,
                        picture=db_player.picture,
                    )
                    session.players.append(player)
                arena.sessions.append(session)
            group.arenas.append(arena)
        for db_manager in db_group.managers:
            manager = GroupByGameUserClientResponse(
                id=db_manager.id,
                user_id=db_manager.user_id,
                user_email=db_manager.user_email,
                first_name=db_manager.first_name,
                last_name=db_manager.last_name
            )
            group.managers.append(manager)
        groups.append(group)
    return groups
