from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_active_membership
from app.models.organization import Membership
from app.models.agent import Agent, AgentType
from app.agents.registry import AgentRegistry

router = APIRouter()


class AnalyzeRequest(BaseModel):
    pass


class SimulateRequest(BaseModel):
    change: str
    metric: str = "response_rate"


@router.post("/analyze")
async def analyze_opportunities(
    request: AnalyzeRequest,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_optimization_agent(membership, db)

    optimization = AgentRegistry.create(
        agent_type="optimization",
        organization_id=membership.organization_id,
        agent_id=agent.id,
        name=agent.name,
        config=agent.config,
    )

    return await optimization.execute({"action": "analyze"}, db)


@router.post("/simulate")
async def simulate_change(
    request: SimulateRequest,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_optimization_agent(membership, db)

    optimization = AgentRegistry.create(
        agent_type="optimization",
        organization_id=membership.organization_id,
        agent_id=agent.id,
        name=agent.name,
        config=agent.config,
    )

    return await optimization.execute(
        {
            "action": "simulate",
            "change": request.change,
            "metric": request.metric,
        },
        db,
    )


async def _get_optimization_agent(membership: Membership, db: AsyncSession) -> Agent:
    result = await db.execute(
        select(Agent).where(
            Agent.organization_id == membership.organization_id,
            Agent.agent_type == AgentType.OPTIMIZATION,
        )
    )
    agent = result.scalar_one_or_none()

    if not agent:
        agent = Agent(
            organization_id=membership.organization_id,
            name="Optimization Agent",
            agent_type=AgentType.OPTIMIZATION,
        )
        db.add(agent)
        await db.flush()

    return agent
