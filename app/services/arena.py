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
from app.payloads.response.ArenaShowByGameResponse import ArenaShowByGameResponse
from app.payloads.response.GroupByGameResponse import GroupByGameResponse, GroupByGameArenaClientResponse, \
    GroupByGameArenaSessionResponse, GroupByGameSessionPlayerClientResponse, GroupByGameUserClientResponse
from app.payloads.response.GroupClientResponse import GroupClientResponse, GroupUserClientResponse, \
    GroupArenaClientResponse, GroupArenaSessionResponse, GroupSessionPlayerClientResponse
from app.payloads.response.SessionCreateResponse import ProjectResponse
from app.services.get_arena import get_arena
from app.services.invite_managers import invite_managers
from app.services.organisation_service import OrganisationServiceClient
from app.services.user_service import UserServiceClient, get_user_service


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


async def get_groups(db: Session, org_id: str):
    db_groups = db.query(models.Group).filter(models.Group.organisation_code == org_id).all()
    groups = []
    for db_group in db_groups:
        group = GroupClientResponse(
            id=db_group.id,
            name=db_group.name,
            managers=[],
            arenas=[],
            games=[]
        )
        for manager in db_group.managers:
            # Fetch user details using the UserServiceClient
            user_details = None
            if (not manager.user_id is None) and manager.user_id != 'None':
                user_details = await get_user_service().get_user_by_id(manager.user_id)

            if user_details is None and (not manager.user_email is None) and manager.user_email != 'None':
                user_details = await get_user_service().get_user_by_email(manager.user_email)

            if user_details:
                group.managers.append(GroupUserClientResponse(
                    id=manager.id,
                    **(dict(user_details)),
                ))
            else:
                group.managers.append(GroupUserClientResponse(
                    id=manager.id,
                    user_id=manager.user_id,
                    user_email=manager.user_email,
                    user_name=f"{manager.first_name} {manager.last_name}",
                ))

        for db_arena in db_group.arenas:
            arena = GroupArenaClientResponse(
                id=db_arena.id,
                name=db_arena.name,
                sessions=[]
            )
            arena_sessions = db.query(ArenaSession).filter(
                ArenaSession.arena_id == arena.id
            )
            for db_session in arena_sessions:
                session = GroupArenaSessionResponse(
                    id=db_session.id,
                    period_type=db_session.period_type,
                    start_time=db_session.start_time,
                    end_time=db_session.end_time,
                    access_status=db_session.access_status,
                    session_status=db_session.session_status,
                    view_access=db_session.view_access,
                    players=[]
                )
                for db_player in db_session.players:
                    # Fetch user details using the UserServiceClient
                    user_details = None
                    if (not db_player.user_id is None) and db_player.user_id != 'None':
                        user_details = await get_user_service().get_user_by_id(db_player.user_id)

                    if user_details is None and (not db_player.user_email is None) and db_player.user_email != 'None':
                        user_details = await get_user_service().get_user_by_email(db_player.user_email)

                    if user_details:
                        player = GroupSessionPlayerClientResponse(
                            **dict(user_details)
                        )
                    else:
                        player = GroupSessionPlayerClientResponse(
                            user_id=db_player.user_id,
                            email=db_player.user_email,
                            first_name=db_player.user_name,
                            last_name=db_player.user_name
                        )

                    session.players.append(player)
                arena.sessions.append(session)
            group.arenas.append(arena)

        for db_game in db_group.games:
            game = ProjectResponse(
                id=db_game.id,
                name=db_game.name,
                description=db_game.description,
                slug=db_game.slug,
                visibility=db_game.visibility,
                activation_status=db_game.activation_status,
                client_id=db_game.client_id,
                client_name=db_game.client_name,
                start_time=db_game.start_time,
                end_time=db_game.end_time
            )
            group.games.append(game)
        groups.append(group)

    return groups


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
async def get_arenas(db: Session, org_id: str):
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
                managers=[]
            )

            for manager in db_group.managers:
                # Fetch user details using the UserServiceClient
                user_details = None
                if (not manager.user_id is None) and manager.user_id != 'None':
                    user_details = await get_user_service().get_user_by_id(manager.user_id)

                if user_details is None and (not manager.user_email is None) and manager.user_email != 'None':
                    user_details = await get_user_service().get_user_by_email(manager.user_email)

                if user_details:
                    group.managers.append(ArenaListGroupUserClientResponse(
                        **(dict(user_details)),
                        picture=manager.picture  # Assuming `picture` is stored in the `manager` object
                    ))
                else:
                    group.managers.append(ArenaListGroupUserClientResponse(
                        user_id=manager.user_id,
                        user_email=manager.user_email,
                        user_name=f"{manager.first_name} {manager.last_name}",
                        picture=manager.picture  # Assuming `picture` is stored in the `manager` object
                    ))

            groups.append(group)
        arena.groups = groups
        dict_players = set()
        players = []
        for session in db_arena.sessions:
            for player in session.players:
                if player.user_email not in dict_players:
                    dict_players.add(player.user_email)
                    # Fetch user details using the UserServiceClient
                    user_details = None
                    if (not player.user_id is None) and player.user_id != 'None':
                        user_details = await get_user_service().get_user_by_id(player.user_id)

                    if user_details is None and (not player.user_email is None) and player.user_email != 'None':
                        user_details = await get_user_service().get_user_by_email(player.user_email)

                    if user_details:
                        players.append(ArenaMembers(
                            **dict(user_details),
                            picture=None
                        ))
                    else:
                        players.append(ArenaMembers(
                            user_id=player.user_id,
                            user_email=player.user_email,
                            user_name=player.user_name,
                            picture=None
                        ))

        arena.players = players
        arenas.append(arena)
    return arenas

async def show_arena(db: Session, arena_id: UUID, org_id: str):
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
            managers=[]
        )

        for manager in db_group.managers:
            # Fetch user details using the UserServiceClient
            user_details = None
            if (not manager.user_id is None) and manager.user_id != 'None':
                user_details = await get_user_service().get_user_by_id(manager.user_id)

            if user_details is None and (not manager.user_email is None) and manager.user_email != 'None':
                user_details = await get_user_service().get_user_by_email(manager.user_email)

            if user_details:
                group.managers.append(ArenaListGroupUserClientResponse(
                    **(dict(user_details)),
                    picture=manager.picture  # Assuming `picture` is stored in the `manager` object
                ))
            else:
                group.managers.append(ArenaListGroupUserClientResponse(
                    user_id=manager.user_id,
                    user_email=manager.user_email,
                    user_name=f"{manager.first_name} {manager.last_name}",
                    picture=manager.picture  # Assuming `picture` is stored in the `manager` object
                ))

        groups.append(group)
    arena.groups = groups
    dict_players = set()
    players = []
    for session in db_arena.sessions:
        for player in session.players:
            if player.user_email not in dict_players:
                dict_players.add(player.user_email)
                user_details = None
                if (not player.user_id is None) and player.user_id != 'None':
                    user_details = await get_user_service().get_user_by_id(player.user_id)

                if user_details is None and (not player.user_email is None) and player.user_email != 'None':
                    user_details = await get_user_service().get_user_by_email(player.user_email)

                if user_details:
                    players.append(ArenaMembers(
                        **dict(user_details),
                        picture=None
                    ))
                else:
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
