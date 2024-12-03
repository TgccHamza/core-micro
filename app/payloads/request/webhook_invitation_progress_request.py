from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

class InvitationUserRequest(BaseModel):
    id: Optional[str] = None

# Enum for possible statuses
class InvitationStatus(str, Enum):
    EMAIL_RECEIVED = "email_received"
    INVITATION_ACCEPTED = "invitation_accepted"

# Enum for possible statuses
class RoleType(str, Enum):
    GAME_MASTER = "game_master"
    PLAYER = "player"
    MANAGER = "manager"
    MODERATOR = "moderator"


class WebhookInvitationProgressRequest(BaseModel):
    status: InvitationStatus
    role: RoleType = RoleType.PLAYER
    session_id: str = Field(..., description="Unique identifier for the session")
    users: list[InvitationUserRequest] = Field(..., description="emails for the session")
