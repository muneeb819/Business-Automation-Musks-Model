from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_active_membership
from app.models.organization import Membership
from app.models.agent import Agent, AgentType
from sqlalchemy import select
from app.agents.registry import AgentRegistry

router = APIRouter()


@router.post("/detect-demand")
async def detect_demand(
    demands: list[dict],
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Agent).where(
            Agent.organization_id == membership.organization_id,
            Agent.agent_type == AgentType.MARKETPLACE,
        )
    )
    agent = result.scalar_one_or_none()

    if not agent:
        from app.models.agent import Agent as AgentModel
        agent = AgentModel(
            organization_id=membership.organization_id,
            name="Marketplace Agent",
            agent_type=AgentType.MARKETPLACE,
        )
        db.add(agent)
        await db.flush()

    marketplace = AgentRegistry.create(
        agent_type="marketplace",
        organization_id=membership.organization_id,
        agent_id=agent.id,
        name=agent.name,
        config=agent.config,
    )

    result = await marketplace.execute(
        {"action": "detect_demand", "demands": demands},
        db,
    )

    surfaced = []
    for demand in result["demands"]:
        approval_result = await marketplace.execute(
            {"action": "surface_for_approval", "demand": demand},
            db,
        )
        surfaced.append(approval_result)

    return {
        "demands_detected": len(demands),
        "surfaced_for_approval": surfaced,
        "message": "Demands surfaced. No outreach sent without Muneeb's approval.",
    }
