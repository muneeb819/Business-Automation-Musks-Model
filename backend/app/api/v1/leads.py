from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.core.deps import get_current_active_membership
from app.models.lead import Lead, LeadStatus, LeadSource
from app.models.company import Company
from app.models.contact import Contact
from app.models.organization import Membership
from app.schemas.lead import (
    LeadCreate,
    LeadResponse,
    LeadDetailResponse,
    LeadListResponse,
    LeadUpdate,
    CompanyCreate,
    CompanyResponse,
    ContactCreate,
    ContactResponse,
)

router = APIRouter()


@router.get("/", response_model=LeadListResponse)
async def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[LeadStatus] = None,
    source: Optional[LeadSource] = None,
    search: Optional[str] = None,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    query = select(Lead).where(
        Lead.organization_id == membership.organization_id,
        Lead.is_deleted == False,
    )

    if status:
        query = query.where(Lead.status == status)
    if source:
        query = query.where(Lead.source == source)
    if search:
        query = query.join(Company, Lead.company_id == Company.id, isouter=True)
        query = query.where(Company.name.ilike(f"%{search}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Lead.created_at.desc())
    result = await db.execute(query)
    leads = result.scalars().all()

    return LeadListResponse(
        leads=[LeadResponse.model_validate(lead) for lead in leads],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{lead_id}", response_model=LeadDetailResponse)
async def get_lead(
    lead_id: UUID,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Lead).where(
            Lead.id == lead_id,
            Lead.organization_id == membership.organization_id,
        )
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadDetailResponse.model_validate(lead)


@router.post("/", response_model=LeadResponse)
async def create_lead(
    lead_data: LeadCreate,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    lead = Lead(
        organization_id=membership.organization_id,
        company_id=lead_data.company_id,
        contact_id=lead_data.contact_id,
        campaign_id=lead_data.campaign_id,
        source=lead_data.source,
        source_detail=lead_data.source_detail,
        source_url=lead_data.source_url,
        personalization_data=lead_data.personalization_data or {},
        tags=lead_data.tags or [],
        notes=lead_data.notes,
    )
    db.add(lead)
    await db.flush()
    return LeadResponse.model_validate(lead)


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    lead_data: LeadUpdate,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Lead).where(
            Lead.id == lead_id,
            Lead.organization_id == membership.organization_id,
        )
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    update_data = lead_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)
    lead.updated_at = datetime.utcnow()

    return LeadResponse.model_validate(lead)


@router.post("/{lead_id}/handoff")
async def create_human_handoff(
    lead_id: UUID,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Lead).where(
            Lead.id == lead_id,
            Lead.organization_id == membership.organization_id,
        )
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead.status = LeadStatus.HUMAN_HANDOFF
    lead.handoff_date = datetime.utcnow()
    lead.assigned_user_id = membership.user_id
    lead.updated_at = datetime.utcnow()

    return {"message": "Human handoff created", "lead_id": str(lead_id)}
