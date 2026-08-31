import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Float, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class ApprovalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ApprovalCategory(enum.Enum):
    AGENT_BEHAVIOR = "agent_behavior"
    BUG_FIX = "bug_fix"
    TYPO = "typo"
    UI_UX = "ui_ux"
    CSS = "css"
    SYSTEM_CONFIG = "system_config"
    OUTREACH = "outreach"
    MARKETING = "marketing"
    OTHER = "other"


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)

    category = Column(SAEnum(ApprovalCategory), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    proposed_fix = Column(Text, nullable=False)
    affected_system = Column(String(255))
    risk_level = Column(String(20), default="low")
    expected_impact = Column(Text)
    evidence = Column(Text)
    rollback_strategy = Column(Text)

    status = Column(SAEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    approver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approval_notes = Column(Text)
    execution_result = Column(JSON)
    executed_at = Column(DateTime)
    resolved_at = Column(DateTime)
    expires_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="approvals")
    requester = relationship("User", foreign_keys=[requester_id])
    approver = relationship("User", foreign_keys=[approver_id])
