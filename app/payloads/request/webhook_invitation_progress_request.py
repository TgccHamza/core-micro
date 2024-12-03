from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

class InvitationUserRequest(BaseModel):
    email: Optional[str] = Field(..., description="emails for the session")
    id: Optional[str] = Field(..., description="ids identifiers for the session")


# Enum for possible statuses
class InvitationStatus(str, Enum):
    EMAIL_RECEIVED = "email_received"  #User has received the email
    INVITATION_ACCEPTED = "invitation_accepted"  # User accepted the invitation

class WebhookInvitationProgressRequest(BaseModel):
    status: InvitationStatus
    session_id: str = Field(..., description="Unique identifier for the session")
    users: list[InvitationUserRequest] = Field(..., description="emails for the session")
