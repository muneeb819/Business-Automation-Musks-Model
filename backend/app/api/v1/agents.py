from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.core.deps import get_current_active_membership
from app.models.agent import Agent, AgentRun, AgentStatus
from app.models.organization import Membership
from app.schemas.agent import (
    AgentCreate,
    AgentResponse,
    AgentHealthScore,
    AgentRunResponse,
)

router = APIRouter()


@router.get("/", response_model=list[AgentResponse])
async def list_agents(
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Agent).where(Agent.organization_id == membership.organization_id)
    )
    return result.scalars().all()


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.organization_id == membership.organization_id,
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    agent = Agent(
        organization_id=membership.organization_id,
        **agent_data.model_dump()
    )
    db.add(agent)
    await db.flush()
    return agent


@router.patch("/{agent_id}/status")
async def update_agent_status(
    agent_id: UUID,
    status: AgentStatus,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.organization_id == membership.organization_id,
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.status = status
    agent.updated_at = datetime.utcnow()
    return {"message": f"Agent status updated to {status}"}


@router.get("/{agent_id}/health", response_model=AgentHealthScore)
async def get_agent_health(
    agent_id: UUID,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.organization_id == membership.organization_id,
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    success_rate = (agent.successful_runs / agent.total_runs * 100) if agent.total_runs > 0 else 100
    error_rate = (agent.failed_runs / agent.total_runs * 100) if agent.total_runs > 0 else 0

    return AgentHealthScore(
        agent_id=agent.id,
        agent_name=agent.name,
        availability=99.9 if agent.status == AgentStatus.ACTIVE else 0,
        execution_success=success_rate,
        task_completion=success_rate,
        latency=95.0,
        error_rate=error_rate,
        output_quality=agent.health_score,
        cost_efficiency=89.0,
        policy_compliance=100.0,
        overall_score=agent.health_score,
    )


@router.get("/{agent_id}/runs", response_model=list[AgentRunResponse])
async def list_agent_runs(
    agent_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.organization_id == membership.organization_id,
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    runs_result = await db.execute(
        select(AgentRun)
        .where(AgentRun.agent_id == agent_id)
        .order_by(AgentRun.started_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return runs_result.scalars().all()
