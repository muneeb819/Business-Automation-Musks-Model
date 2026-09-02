"""
Lead and company/contact schemas for CRM operations.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.lead import LeadStatus, LeadSource


class LeadCreate(BaseModel):
    """Schema for creating a new lead."""
    company_id: Optional[UUID] = Field(None, description="Associated company ID")
    contact_id: Optional[UUID] = Field(None, description="Associated contact ID")
    campaign_id: Optional[UUID] = Field(None, description="Associated campaign ID")
    source: LeadSource = Field(..., description="Lead source")
    source_detail: Optional[str] = Field(None, description="Additional source details")
    source_url: Optional[str] = Field(None, description="URL where lead was found")
    personalization_data: Optional[dict] = Field(default_factory=dict, description="Personalization data")
    tags: Optional[List[str]] = Field(default_factory=list, description="Lead tags")
    notes: Optional[str] = Field(None, description="Lead notes")


class LeadResponse(BaseModel):
    """Schema for lead in list responses."""
    id: UUID = Field(..., description="Lead ID")
    organization_id: UUID = Field(..., description="Organization ID")
    status: LeadStatus = Field(..., description="Lead status")
    fit_score: float = Field(default=0, description="Lead fit score")
    lead_score: float = Field(default=0, description="Lead score")
    intent_score: float = Field(default=0, description="Intent score")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class LeadDetailResponse(LeadResponse):
    """Schema for detailed lead response."""
    company_id: Optional[UUID] = Field(None, description="Associated company ID")
    contact_id: Optional[UUID] = Field(None, description="Associated contact ID")
    source: LeadSource = Field(..., description="Lead source")
    notes: Optional[str] = Field(None, description="Lead notes")
    tags: List[str] = Field(default_factory=list, description="Lead tags")
    outreach_count: int = Field(default=0, description="Number of outreach attempts")
    last_outreach_date: Optional[datetime] = Field(None, description="Last outreach timestamp")
    personalization_data: dict = Field(default_factory=dict, description="Personalization data")


class LeadUpdate(BaseModel):
    """Schema for updating a lead."""
    status: Optional[LeadStatus] = Field(None, description="New status")
    fit_score: Optional[float] = Field(None, description="Updated fit score")
    lead_score: Optional[float] = Field(None, description="Updated lead score")
    intent_score: Optional[float] = Field(None, description="Updated intent score")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    notes: Optional[str] = Field(None, description="Updated notes")


class LeadListResponse(BaseModel):
    """Schema for paginated lead list response."""
    leads: List[LeadResponse] = Field(..., description="List of leads")
    total: int = Field(..., description="Total lead count")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")


class CompanyCreate(BaseModel):
    """Schema for creating a company."""
    name: str = Field(..., description="Company name")
    domain: Optional[str] = Field(None, description="Company domain")
    industry: Optional[str] = Field(None, description="Industry classification")
    location: Optional[str] = Field(None, description="Company location")
    website: Optional[str] = Field(None, description="Company website URL")
    employee_count: Optional[int] = Field(None, description="Number of employees")


class CompanyResponse(BaseModel):
    """Schema for company in responses."""
    id: UUID = Field(..., description="Company ID")
    name: str = Field(..., description="Company name")
    domain: Optional[str] = Field(None, description="Company domain")
    industry: Optional[str] = Field(None, description="Industry classification")
    location: Optional[str] = Field(None, description="Company location")
    website: Optional[str] = Field(None, description="Company website")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class ContactCreate(BaseModel):
    """Schema for creating a contact."""
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: Optional[str] = Field(None, description="Email address")
    title: Optional[str] = Field(None, description="Job title")
    phone: Optional[str] = Field(None, description="Phone number")
    company_id: Optional[UUID] = Field(None, description="Associated company ID")


class ContactResponse(BaseModel):
    """Schema for contact in responses."""
    id: UUID = Field(..., description="Contact ID")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: Optional[str] = Field(None, description="Email address")
    title: Optional[str] = Field(None, description="Job title")
    company_id: Optional[UUID] = Field(None, description="Associated company ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
