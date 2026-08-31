from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ApprovalCategory(str, Enum):
    AGENT_BEHAVIOR = "agent_behavior"
    BUG_FIX = "bug_fix"
    TYPO = "typo"
    UI_UX = "ui_ux"
    CSS = "css"
    SYSTEM_CONFIG = "system_config"
    OUTREACH = "outreach"
    MARKETING = "marketing"
    OTHER = "other"


class ApprovalCreate(BaseModel):
    category: ApprovalCategory
    title: str
    description: str
    proposed_fix: str
    affected_system: Optional[str] = None
    risk_level: str = "low"
    expected_impact: Optional[str] = None
    evidence: Optional[str] = None
    rollback_strategy: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: UUID
    category: ApprovalCategory
    title: str
    description: str
    proposed_fix: str
    affected_system: Optional[str] = None
    risk_level: str
    status: ApprovalStatus
    created_at: str
    resolved_at: Optional[str] = None

    class Config:
        from_attributes = True


class ApprovalAction(BaseModel):
    action: str
    notes: Optional[str] = None


class ApprovalListResponse(BaseModel):
    approvals: List[ApprovalResponse]
    total: int
    page: int
    page_size: int
