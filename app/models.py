import uuid
from datetime import datetime

from sqlalchemy import Column, String, Enum, Integer, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from app.enums import AccessStatus, PeriodType, SessionStatus, ViewAccess, ActivationStatus, GameType, PlayingType, \
    ModuleType


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), index=True)
    description = Column(String(255), index=True)
    db_index = Column(String(36), index=True)
    slug = Column(String(255), unique=True, index=True)
    visibility = Column(String(50), default="public")  # Default visibility is public
    activation_status = Column(Enum(ActivationStatus), default=ActivationStatus.ACTIVE)
    game_type = Column(Enum(GameType), default=GameType.DIGITAL)
    playing_type = Column(Enum(PlayingType), default=PlayingType.SOLO)
    client_id = Column(String(36), nullable=True, index=True)
    organisation_code = Column(String(36), nullable=True, index=True)
    client_name = Column(String(255), nullable=True, index=True)  # Client name for easy access
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    module_game_id = Column(String(36), nullable=True, index=True)
    module_gamemaster_id = Column(String(36), nullable=True)
    module_super_game_master_id = Column(String(36), nullable=True)
    tags = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, nullable=True, default=lambda: datetime.now())

    # Updated relationship with primaryjoin
    modules = relationship(
        "ProjectModule",
        primaryjoin="Project.id == ProjectModule.project_id",
        back_populates="project",
        foreign_keys='ProjectModule.project_id',
        viewonly=True
    )

    groups = relationship("Group", secondary="group_projects",
                          primaryjoin="Project.id == GroupProjects.project_id",
                          secondaryjoin="Group.id == GroupProjects.group_id",
                          back_populates="games",
                          foreign_keys='[GroupProjects.group_id, GroupProjects.project_id]',
                          viewonly=True)

    arena_sessions = relationship(
        "ArenaSession",
        primaryjoin="Project.id == ArenaSession.project_id",
        back_populates="project",
        foreign_keys='ArenaSession.project_id',
        viewonly=True
    )


class ProjectModule(Base):
    __tablename__ = "project_modules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), index=True)
    description = Column(String(255), index=True)
    type = Column(Enum(ModuleType), default=ModuleType.EXTENSION)
    project_id = Column(String(36), index=True)  # No ForeignKey constraint
    template_code = Column(String(36), index=True)  # No ForeignKey constraint
    # New fields
    order = Column(Integer, nullable=False, default=0)  # Module order within the project

    # Updated relationship with primaryjoin
    project = relationship(
        "Project",
        foreign_keys=[project_id],
        primaryjoin="ProjectModule.project_id == Project.id",
        viewonly=True
    )


# ProjectFavorite model
class ProjectFavorite(Base):
    __tablename__ = "project_favorites"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), index=True)  # No ForeignKey constraint
    user_id = Column(String(36), nullable=False, index=True)  # Assuming each user has a unique ID

    # Relationships
    project = relationship(
        "Project",
        foreign_keys=[project_id],
        primaryjoin="ProjectFavorite.project_id == Project.id",
        viewonly=True
    )


# Group model
class Group(Base):
    __tablename__ = "groups"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    organisation_code = Column(String(36), nullable=True, index=True)

    # Relationships
    managers = relationship("GroupUsers", primaryjoin="GroupUsers.group_id == Group.id",
                            foreign_keys='GroupUsers.group_id', back_populates="group",
                            viewonly=True)
    games = relationship("Project", secondary="group_projects",
                         primaryjoin="GroupProjects.group_id == Group.id",
                         secondaryjoin="GroupProjects.project_id == Project.id",
                         back_populates="groups",
                         foreign_keys='[GroupProjects.group_id, GroupProjects.project_id]',
                         viewonly=True)
    arenas = relationship("Arena", secondary="group_arenas",
                          primaryjoin="GroupArenas.group_id == Group.id",
                          secondaryjoin="GroupArenas.arena_id == Arena.id",
                          foreign_keys='[GroupArenas.group_id, GroupArenas.arena_id, GroupArenas.user_id]',
                          back_populates="groups",
                          viewonly=True)


# GroupUsers model
class GroupUsers(Base):
    __tablename__ = "group_users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String(36))  # No ForeignKey constraint
    user_id = Column(String(36))  # No ForeignKey constraint
    user_email = Column(String(255), nullable=True)  # No ForeignKey constraint
    first_name = Column(String(150), nullable=True)  # No ForeignKey constraint
    last_name = Column(String(150), nullable=True)  # No ForeignKey constraint
    picture = Column(String(255), nullable=True)  # No ForeignKey constraint

    # Relationships
    group = relationship(
        "Group",
        foreign_keys=[group_id],
        primaryjoin="GroupUsers.group_id == Group.id",
        viewonly=True
    )


#     user = relationship("User")

# GroupProjects model
class GroupProjects(Base):
    __tablename__ = "group_projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String(36))  # No ForeignKey constraint
    project_id = Column(String(36))  # No ForeignKey constraint

    # Relationships


#     group = relationship("Group", back_populates="projects")
#     project = relationship("Project", primaryjoin="GroupProjects.project_id == Project.id")

# GroupArenas model
class GroupArenas(Base):
    __tablename__ = "group_arenas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String(36))  # No ForeignKey constraint
    arena_id = Column(String(36))  # No ForeignKey constraint
    user_id = Column(String(36), nullable=True)  # No ForeignKey constraint

    # Relationships


#     group = relationship("Group", back_populates="arenas")
#     arena = relationship("Arena", primaryjoin="GroupArenas.arena_id == Arena.id")

# Arena model
class Arena(Base):
    __tablename__ = "arenas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    organisation_code = Column(String(36), nullable=True, index=True)

    # Relationships
    sessions = relationship("ArenaSession",
                            foreign_keys="ArenaSession.arena_id",
                            primaryjoin="ArenaSession.arena_id == Arena.id", back_populates="arena",
                            viewonly=True)
    groups = relationship("Group", secondary="group_arenas",
                          primaryjoin="GroupArenas.group_id == Group.id",
                          secondaryjoin="GroupArenas.arena_id == Arena.id",
                          foreign_keys='[GroupArenas.group_id, GroupArenas.arena_id]',
                          back_populates="arenas",
                          viewonly=True)


# ArenaSession model
class ArenaSession(Base):
    __tablename__ = "arena_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organisation_code = Column(String(36), nullable=True, index=True)
    arena_id = Column(String(36))  # No ForeignKey constraint
    project_id = Column(String(36))  # No ForeignKey constraint
    period_type = Column(Enum(PeriodType), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    access_status = Column(Enum(AccessStatus), nullable=False)
    session_status = Column(Enum(SessionStatus), nullable=False)
    view_access = Column(Enum(ViewAccess), nullable=False)
    super_game_master_id = Column(String(36), nullable=True)
    player_module_id = Column(String(36), nullable=True)
    gamemaster_module_id = Column(String(36), nullable=True)
    super_game_master_module_id = Column(String(36), nullable=True)

    # Relationships
    project = relationship("Project",
                           foreign_keys="ArenaSession.project_id",
                           primaryjoin="ArenaSession.project_id == Project.id",
                           viewonly=True)

    arena = relationship("Arena",
                         foreign_keys="ArenaSession.arena_id",
                         primaryjoin="ArenaSession.arena_id == Arena.id", back_populates="sessions",
                         viewonly=True)

    players = relationship("ArenaSessionPlayers",
                           foreign_keys="ArenaSessionPlayers.session_id",
                           primaryjoin="ArenaSessionPlayers.session_id == ArenaSession.id", back_populates="session",
                           viewonly=True)


class ArenaSessionTeam(Base):
    __tablename__ = "arena_session_teams"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    session_id = Column(String(36))  # No ForeignKey constraint


class ArenaSessionTeamGameMaster(Base):
    __tablename__ = "arena_session_team_game_masters"

    team_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False)


# ArenaSessionPlayers model
class ArenaSessionPlayers(Base):
    __tablename__ = "arena_session_players"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organisation_code = Column(String(36), nullable=True, index=True)
    session_id = Column(String(36))  # No ForeignKey constraint
    team_id = Column(String(36), nullable=True)  # No ForeignKey constraint
    user_id = Column(String(36), nullable=True)  # No ForeignKey constraint
    user_email = Column(String(255), nullable=True)
    module_id = Column(String(36))  # No ForeignKey constraint

    module = relationship("ProjectModule",
                          foreign_keys="ArenaSessionPlayers.module_id",
                          primaryjoin="ArenaSessionPlayers.module_id == ProjectModule.id",
                          viewonly=True)

    # Relationships
    session = relationship("ArenaSession",
                           foreign_keys="ArenaSessionPlayers.session_id",
                           primaryjoin="ArenaSessionPlayers.session_id == ArenaSession.id", back_populates="players",
                           viewonly=True)
