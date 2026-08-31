from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.core.deps import get_current_active_membership
from app.models.campaign import Campaign
from app.models.organization import Membership

router = APIRouter()


@router.get("/")
async def list_campaigns(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign)
        .where(Campaign.organization_id == membership.organization_id)
        .order_by(Campaign.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    campaigns = result.scalars().all()

    total = await db.execute(
        select(func.count()).select_from(Campaign).where(
            Campaign.organization_id == membership.organization_id
        )
    )

    return {
        "campaigns": [{
            "id": str(c.id),
            "name": c.name,
            "description": c.description,
            "campaign_type": c.campaign_type,
            "status": c.status,
            "target_industries": c.target_industries,
            "target_platforms": c.target_platforms,
            "start_date": c.start_date.isoformat() if c.start_date else None,
            "end_date": c.end_date.isoformat() if c.end_date else None,
            "budget": c.budget,
            "spend": c.spend,
            "created_at": c.created_at.isoformat(),
        } for c in campaigns],
        "total": total.scalar(),
        "page": page,
        "page_size": page_size,
    }


@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: UUID,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.organization_id == membership.organization_id,
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.post("/")
async def create_campaign(
    campaign_data: dict,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    campaign = Campaign(
        organization_id=membership.organization_id,
        **campaign_data
    )
    db.add(campaign)
    await db.flush()
    return campaign


@router.patch("/{campaign_id}")
async def update_campaign(
    campaign_id: UUID,
    campaign_data: dict,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.organization_id == membership.organization_id,
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    update_data = {k: v for k, v in campaign_data.items() if k != "id"}
    for field, value in update_data.items():
        setattr(campaign, field, value)
    campaign.updated_at = datetime.utcnow()

    return campaign
