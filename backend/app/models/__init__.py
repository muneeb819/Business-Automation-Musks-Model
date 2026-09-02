"""
Database models for all entities.
"""

from app.models.user import User
from app.models.organization import Organization, Membership
from app.models.crm import (
    Lead,
    LeadStatus,
    LeadSource,
    Company,
    Contact,
    Campaign,
    Activity,
    OutreachMessage,
    Conversation,
    ConversationMessage,
)
from app.models.approval import Approval, ApprovalStatus, ApprovalAction
from app.models.agent import Agent, AgentType, AgentStatus
from app.models.notification import Notification, NotificationType
from app.models.integration import Integration
from app.models.knowledge import Knowledge
from app.models.marketing import MarketingCampaign, PromotionChannel
from app.models.daily_snapshot import DailySnapshot

__all__ = [
    "User",
    "Organization",
    "Membership",
    "Lead",
    "LeadStatus",
    "LeadSource",
    "Company",
    "Contact",
    "Campaign",
    "Activity",
    "OutreachMessage",
    "Conversation",
    "ConversationMessage",
    "Approval",
    "ApprovalStatus",
    "ApprovalAction",
    "Agent",
    "AgentType",
    "AgentStatus",
    "Notification",
    "NotificationType",
    "Integration",
    "Knowledge",
    "MarketingCampaign",
    "PromotionChannel",
    "DailySnapshot",
]
