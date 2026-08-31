from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from uuid import UUID
from app.core.database import get_db
from app.core.deps import get_current_active_membership
from app.models.marketing import MarketingActivity
from app.models.organization import Membership

router = APIRouter()


@router.get("/")
async def list_marketing_activity(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    agent_type: Optional[str] = None,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    query = select(MarketingActivity).where(
        MarketingActivity.organization_id == membership.organization_id
    )

    if agent_type:
        query = query.where(MarketingActivity.agent_type == agent_type)

    total_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_query)).scalar()

    result = await db.execute(
        query.order_by(MarketingActivity.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    activities = result.scalars().all()

    return {
        "activities": [{
            "id": str(a.id),
            "agent_type": a.agent_type.value if hasattr(a.agent_type, "value") else str(a.agent_type),
            "platform": a.platform,
            "content_type": a.content_type,
            "title": a.title,
            "views": a.views,
            "engagement_rate": a.engagement_rate,
            "clicks": a.clicks,
            "leads_attributed": a.leads_attributed,
            "spend": a.spend,
            "status": a.status,
            "created_at": a.created_at.isoformat(),
        } for a in activities],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/performance")
async def marketing_performance(
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MarketingActivity).where(
            MarketingActivity.organization_id == membership.organization_id
        )
    )
    activities = result.scalars().all()

    total_views = sum(a.views or 0 for a in activities)
    total_clicks = sum(a.clicks or 0 for a in activities)
    total_leads = sum(a.leads_attributed or 0 for a in activities)
    total_spend = sum(a.spend or 0 for a in activities)

    return {
        "total_views": total_views,
        "total_clicks": total_clicks,
        "total_leads_attributed": total_leads,
        "total_spend": total_spend,
        "click_rate": round((total_clicks / total_views * 100), 2) if total_views else 0,
        "cost_per_lead": round((total_spend / total_leads), 2) if total_leads else 0,
        "activity_count": len(activities),
    }
