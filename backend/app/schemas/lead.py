from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    DISQUALIFIED = "disqualified"
    READY_TO_CLOSE = "ready_to_close"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    HUMAN_HANDOFF = "human_handoff"


class LeadSource(str, Enum):
    HUNTING = "hunting"
    LINKEDIN_ORGANIC = "linkedin_organic"
    PAID_AD = "paid_ad"
    SEO = "seo"
    REFERRAL = "referral"
    INBOUND_FORM = "inbound_form"
    MANUAL_IMPORT = "manual_import"
    MARKETPLACE = "marketplace"


class CompanyCreate(BaseModel):
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    size: Optional[str] = None
    employee_count: Optional[int] = None
    description: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None


class CompanyResponse(BaseModel):
    id: UUID
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class ContactCreate(BaseModel):
    company_id: Optional[UUID] = None
    first_name: str
    last_name: str
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    is_decision_maker: bool = False


class ContactResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    title: Optional[str] = None
    email: Optional[str] = None
    is_decision_maker: bool
    is_verified: bool
    created_at: str

    class Config:
        from_attributes = True


class LeadCreate(BaseModel):
    company_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    source: LeadSource
    source_detail: Optional[str] = None
    source_url: Optional[str] = None
    personalization_data: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []
    notes: Optional[str] = None


class LeadResponse(BaseModel):
    id: UUID
    company_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    source: LeadSource
    status: LeadStatus
    fit_score: float
    lead_score: float
    outreach_count: int
    created_at: str
    last_activity_date: Optional[str] = None

    class Config:
        from_attributes = True


class LeadDetailResponse(LeadResponse):
    company: Optional[CompanyResponse] = None
    contact: Optional[ContactResponse] = None
    scoring_explanation: Optional[Dict[str, Any]] = None
    personalization_data: Optional[Dict[str, Any]] = None


class LeadListResponse(BaseModel):
    leads: List[LeadResponse]
    total: int
    page: int
    page_size: int


class LeadUpdate(BaseModel):
    status: Optional[LeadStatus] = None
    assigned_user_id: Optional[UUID] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
