import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class NotificationType(enum.Enum):
    READY_TO_CLOSE = "ready_to_close"
    APPROVAL_NEEDED = "approval_needed"
    SYSTEM_ISSUE = "system_issue"
    HUMAN_HANDOFF = "human_handoff"
    NEW_REPLY = "new_reply"
    AGENT_FAILURE = "agent_failure"
    STRATEGY_RECOMMENDATION = "strategy_recommendation"


class NotificationChannel(enum.Enum):
    PUSH = "push"
    DASHBOARD = "dashboard"
    EMAIL = "email"
    SLACK = "slack"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    type = Column(SAEnum(NotificationType), nullable=False)
    reference_id = Column(UUID(as_uuid=True))
    reference_type = Column(String(50))
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    channel = Column(SAEnum(NotificationChannel), default=NotificationChannel.DASHBOARD)
    is_read = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)
    meta_data = Column(JSON, default=dict)

    user = relationship("User")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    actor_type = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(UUID(as_uuid=True))
    before_state = Column(JSON)
    after_state = Column(JSON)
    result = Column(String(50))
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    request_id = Column(String(100))
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class DailySnapshot(Base):
    __tablename__ = "daily_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    leads_found = Column(Integer, default=0)
    leads_contacted = Column(Integer, default=0)
    replies_received = Column(Integer, default=0)
    ready_to_close_count = Column(Integer, default=0)
    deals_closed_won = Column(Integer, default=0)
    deals_closed_lost = Column(Integer, default=0)
    marketing_spend = Column(Integer, default=0)
    marketing_traffic = Column(Integer, default=0)
    pending_approvals = Column(Integer, default=0)
    system_alerts = Column(Integer, default=0)
    ai_cost = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
