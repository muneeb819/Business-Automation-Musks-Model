from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.approval import ApprovalStatus, ApprovalCategory


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
    created_at: datetime
    resolved_at: Optional[datetime] = None

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
