# Define the Enum for periodType
from enum import Enum as PyEnum


class ModuleType(PyEnum):
    GAME = "game"
    EXTENSION = "extension"


class ModuleForType(PyEnum):
    ALL = "all"
    PLAYER = "player"
    GAMEMASTER = "gamemaster"
    MODERATOR = "moderator"
    MANAGER = "manager"
    OWNER = "owner"


class GameType(PyEnum):
    DIGITAL = "digital"
    PHYGITAL = "phygital"
    PHYSICAL = "physical"


class PlayingType(PyEnum):
    SOLO = "solo"
    TEAM = "team"


# Define Enum for accessType
class AccessStatus(PyEnum):
    AUTH = "auth"
    GUEST = "guest"


class PeriodType(PyEnum):
    FREE = "free"
    RANGE = "range"


class SessionStatus(PyEnum):
    PENDING = "pending"
    PLAYING = "playing"
    ENDED = "ended"


class ViewAccess(PyEnum):
    ALL = "all"
    GAME = "game"
    SESSION = "session"
    NONE = "none"


class ActivationStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class EmailStatus(PyEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
