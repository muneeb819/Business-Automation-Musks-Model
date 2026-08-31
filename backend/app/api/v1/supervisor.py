from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_active_membership
from app.models.organization import Membership
from app.models.agent import Agent, AgentType
from sqlalchemy import select
from app.agents.registry import AgentRegistry

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


class CommandRequest(BaseModel):
    command: str
    is_destructive: bool = False
    confirmed: bool = False


@router.post("/query")
async def supervisor_query(
    request: QueryRequest,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Agent).where(
            Agent.organization_id == membership.organization_id,
            Agent.agent_type == AgentType.SUPERVISOR,
        )
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="Supervisor agent not found for this organization")

    supervisor = AgentRegistry.create(
        agent_type="supervisor",
        organization_id=membership.organization_id,
        agent_id=agent.id,
        name=agent.name,
        config=agent.config,
    )

    return await supervisor.execute({"action": "query", "question": request.question})


@router.post("/command")
async def supervisor_command(
    request: CommandRequest,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Agent).where(
            Agent.organization_id == membership.organization_id,
            Agent.agent_type == AgentType.SUPERVISOR,
        )
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="Supervisor agent not found for this organization")

    supervisor = AgentRegistry.create(
        agent_type="supervisor",
        organization_id=membership.organization_id,
        agent_id=agent.id,
        name=agent.name,
        config=agent.config,
    )

    return await supervisor.execute({
        "action": "execute_command",
        "command": request.command,
        "is_destructive": request.is_destructive,
        "confirmed": request.confirmed,
    })


@router.get("/digest")
async def daily_digest(
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Agent).where(
            Agent.organization_id == membership.organization_id,
            Agent.agent_type == AgentType.SUPERVISOR,
        )
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="Supervisor agent not found for this organization")

    supervisor = AgentRegistry.create(
        agent_type="supervisor",
        organization_id=membership.organization_id,
        agent_id=agent.id,
        name=agent.name,
        config=agent.config,
    )

    return await supervisor.execute({"action": "daily_digest"})
