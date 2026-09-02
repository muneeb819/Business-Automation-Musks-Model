from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
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
import logging

logger = logging.getLogger(__name__)

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
    """List leads with pagination and filtering."""
    try:
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
    except Exception as e:
        logger.error(f"Error listing leads: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve leads",
        )


@router.get("/{lead_id}", response_model=LeadDetailResponse)
async def get_lead(
    lead_id: UUID,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific lead by ID."""
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lead: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve lead",
        )


@router.post("/", response_model=LeadResponse)
async def create_lead(
    lead_data: LeadCreate,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    """Create a new lead."""
    try:
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
            discovery_date=datetime.now(timezone.utc),
        )
        db.add(lead)
        await db.flush()
        logger.info(f"Created new lead: {lead.id}")
        return LeadResponse.model_validate(lead)
    except Exception as e:
        logger.error(f"Error creating lead: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create lead",
        )


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    lead_data: LeadUpdate,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing lead."""
    try:
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
        lead.updated_at = datetime.now(timezone.utc)

        await db.flush()
        logger.info(f"Updated lead: {lead_id}")
        return LeadResponse.model_validate(lead)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lead: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update lead",
        )


@router.post("/{lead_id}/handoff")
async def create_human_handoff(
    lead_id: UUID,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    """Create human handoff for a lead - HARD LOCK the Outreach Agent.

    KEY INVARIANT: Once a lead is handed off, the Outreach Agent is permanently
    locked and cannot perform any further automated actions on this lead.
    """
    try:
        result = await db.execute(
            select(Lead).where(
                Lead.id == lead_id,
                Lead.organization_id == membership.organization_id,
            )
        )
        lead = result.scalar_one_or_none()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        # Set lead to HUMAN_HANDOFF status - this is a HARD LOCK
        lead.status = LeadStatus.HUMAN_HANDOFF
        lead.handoff_date = datetime.now(timezone.utc)
        lead.assigned_user_id = membership.user_id
        lead.updated_at = datetime.now(timezone.utc)

        # CRITICAL: Flush to ensure changes are written to session
        await db.flush()
        logger.warning(
            f"Lead {lead_id} set to HUMAN_HANDOFF by {membership.user_id} - Outreach Agent LOCKED"
        )

        return {
            "message": "Human handoff created. Automated outreach LOCKED.",
            "lead_id": str(lead_id),
            "status": lead.status.value,
            "handoff_date": lead.handoff_date.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating human handoff: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create human handoff",
        )
