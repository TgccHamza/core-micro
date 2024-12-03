from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

class InvitationUserRequest(BaseModel):
    email: Optional[str] = None
    id: Optional[str] = None


# Enum for possible statuses
class InvitationStatus(str, Enum):
    EMAIL_RECEIVED = "email_received"  #User has received the email
    INVITATION_ACCEPTED = "invitation_accepted"  # User accepted the invitation

# Enum for possible statuses
class RoleType(str, Enum):
    GAME_MASTER = "game_master"  #User has received the email
    PLAYER = "player"  # User accepted the invitation
    MANAGER = "manager"  # User accepted the invitation
    MODERATOR = "moderator"  # User accepted the invitation


class WebhookInvitationProgressRequest(BaseModel):
    status: InvitationStatus
    role: RoleType = RoleType.PLAYER
    session_id: str = Field(..., description="Unique identifier for the session")
    users: list[InvitationUserRequest] = Field(..., description="emails for the session")
