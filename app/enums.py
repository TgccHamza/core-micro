
# Define the Enum for periodType
from enum import Enum as PyEnum

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
    ALL="all"
    GAME="game"
    SESSION="session"
    NONE="none"

class ActivationStatus(PyEnum):
    ACTIVE = "active"
    DESACTIVE = "desactive"
