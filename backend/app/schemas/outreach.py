"""
Outreach agent schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class OutreachProposalRequest(BaseModel):
    """Schema for generating an outreach proposal."""
    lead_id: UUID = Field(..., description="Lead ID to generate proposal for")


class OutreachSendRequest(BaseModel):
    """Schema for sending outreach message."""
    lead_id: UUID = Field(..., description="Lead ID to contact")
    content: str = Field(..., description="Message content")
    channel: str = Field(default="email", description="Communication channel (email, linkedin, etc)")


class OutreachReplyRequest(BaseModel):
    """Schema for checking and handling lead reply."""
    lead_id: UUID = Field(..., description="Lead ID that replied")
    has_reply: bool = Field(default=False, description="Whether lead replied")
    reply_content: Optional[str] = Field(None, description="Reply message content")
    channel: Optional[str] = Field(None, description="Channel where reply was received")
