from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.deps import get_current_active_membership
from app.models.lead import Lead, LeadStatus
from app.models.agent import Agent, AgentStatus
from app.models.approval import Approval, ApprovalStatus
from app.models.marketing import MarketingActivity
from app.models.notification import Notification
from app.models.organization import Membership
from app.models.daily_snapshot import DailySnapshot

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    org_id = membership.organization_id

    leads_total = await db.execute(
        select(func.count()).select_from(Lead).where(Lead.organization_id == org_id)
    )
    leads_contacted = await db.execute(
        select(func.count()).select_from(Lead).where(
            Lead.organization_id == org_id,
            Lead.status.in_([LeadStatus.CONTACTED, LeadStatus.ENGAGED, LeadStatus.READY_TO_CLOSE])
        )
    )
    leads_engaged = await db.execute(
        select(func.count()).select_from(Lead).where(
            Lead.organization_id == org_id,
            Lead.status == LeadStatus.ENGAGED
        )
    )
    leads_ready_to_close = await db.execute(
        select(func.count()).select_from(Lead).where(
            Lead.organization_id == org_id,
            Lead.status == LeadStatus.READY_TO_CLOSE
        )
    )
    leads_won = await db.execute(
        select(func.count()).select_from(Lead).where(
            Lead.organization_id == org_id,
            Lead.status == LeadStatus.CLOSED_WON
        )
    )
    leads_lost = await db.execute(
        select(func.count()).select_from(Lead).where(
            Lead.organization_id == org_id,
            Lead.status == LeadStatus.CLOSED_LOST
        )
    )
    human_handoffs = await db.execute(
        select(func.count()).select_from(Lead).where(
            Lead.organization_id == org_id,
            Lead.status == LeadStatus.HUMAN_HANDOFF
        )
    )

    agents_active = await db.execute(
        select(func.count()).select_from(Agent).where(
            Agent.organization_id == org_id,
            Agent.status == AgentStatus.ACTIVE
        )
    )
    agents_failed = await db.execute(
        select(func.count()).select_from(Agent).where(
            Agent.organization_id == org_id,
            Agent.status == AgentStatus.FAILED
        )
    )

    pending_approvals = await db.execute(
        select(func.count()).select_from(Approval).where(
            Approval.organization_id == org_id,
            Approval.status == ApprovalStatus.PENDING
        )
    )

    unread_notifications = await db.execute(
        select(func.count()).select_from(Notification).where(
            Notification.organization_id == org_id,
            Notification.is_read == False
        )
    )

    return {
        "leads": {
            "total": leads_total.scalar(),
            "contacted": leads_contacted.scalar(),
            "engaged": leads_engaged.scalar(),
            "ready_to_close": leads_ready_to_close.scalar(),
            "won": leads_won.scalar(),
            "lost": leads_lost.scalar(),
            "human_handoffs": human_handoffs.scalar(),
        },
        "agents": {
            "active": agents_active.scalar(),
            "failed": agents_failed.scalar(),
        },
        "approvals": {
            "pending": pending_approvals.scalar(),
        },
        "notifications": {
            "unread": unread_notifications.scalar(),
        },
    }


@router.get("/pipeline")
async def get_pipeline_summary(
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    org_id = membership.organization_id

    pipeline = {}
    for status in LeadStatus:
        count_result = await db.execute(
            select(func.count()).select_from(Lead).where(
                Lead.organization_id == org_id,
                Lead.status == status,
            )
        )
        pipeline[status.value] = count_result.scalar()

    return pipeline


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 20,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    from app.models.crm import Activity

    result = await db.execute(
        select(Activity)
        .join(Lead, Activity.lead_id == Lead.id)
        .where(Lead.organization_id == membership.organization_id)
        .order_by(Activity.created_at.desc())
        .limit(limit)
    )
    activities = result.scalars().all()

    return [
        {
            "id": str(a.id),
            "lead_id": str(a.lead_id),
            "agent_name": a.agent_name,
            "action_type": a.action_type,
            "channel": a.channel,
            "summary": a.summary,
            "created_at": a.created_at.isoformat(),
        }
        for a in activities
    ]
