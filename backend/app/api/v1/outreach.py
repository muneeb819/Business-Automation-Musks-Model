from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_active_membership
from app.models.organization import Membership
from app.models.agent import Agent, AgentType
from app.models.lead import Lead
from app.agents.registry import AgentRegistry

router = APIRouter()


class GenerateProposalRequest(BaseModel):
    lead_id: UUID


class SendOutreachRequest(BaseModel):
    lead_id: UUID
    content: str
    channel: str = "email"


class CheckReplyRequest(BaseModel):
    lead_id: UUID
    has_reply: bool = False
    reply_content: Optional[str] = None
    channel: Optional[str] = None


@router.post("/generate-proposal")
async def generate_proposal(
    request: GenerateProposalRequest,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Agent).where(
            Agent.organization_id == membership.organization_id,
            Agent.agent_type == AgentType.OUTREACH,
        )
    )
    agent = result.scalar_one_or_none()

    if not agent:
        from app.models.agent import Agent as AgentModel
        agent = AgentModel(
            organization_id=membership.organization_id,
            name="Outreach Agent",
            agent_type=AgentType.OUTREACH,
        )
        db.add(agent)
        await db.flush()

    outreach = AgentRegistry.create(
        agent_type="outreach",
        organization_id=membership.organization_id,
        agent_id=agent.id,
        name=agent.name,
        config=agent.config,
    )

    return await outreach.execute(
        {"action": "generate_proposal", "lead_id": str(request.lead_id)},
        db,
    )


@router.post("/send")
async def send_outreach(
    request: SendOutreachRequest,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Agent).where(
            Agent.organization_id == membership.organization_id,
            Agent.agent_type == AgentType.OUTREACH,
        )
    )
    agent = result.scalar_one_or_none()

    if not agent:
        from app.models.agent import Agent as AgentModel
        agent = AgentModel(
            organization_id=membership.organization_id,
            name="Outreach Agent",
            agent_type=AgentType.OUTREACH,
        )
        db.add(agent)
        await db.flush()

    outreach = AgentRegistry.create(
        agent_type="outreach",
        organization_id=membership.organization_id,
        agent_id=agent.id,
        name=agent.name,
        config=agent.config,
    )

    return await outreach.execute(
        {
            "action": "send_outreach",
            "lead_id": str(request.lead_id),
            "content": request.content,
            "channel": request.channel,
        },
        db,
    )


@router.post("/check-reply")
async def check_reply(
    request: CheckReplyRequest,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Agent).where(
            Agent.organization_id == membership.organization_id,
            Agent.agent_type == AgentType.OUTREACH,
        )
    )
    agent = result.scalar_one_or_none()

    if not agent:
        from app.models.agent import Agent as AgentModel
        agent = AgentModel(
            organization_id=membership.organization_id,
            name="Outreach Agent",
            agent_type=AgentType.OUTREACH,
        )
        db.add(agent)
        await db.flush()

    outreach = AgentRegistry.create(
        agent_type="outreach",
        organization_id=membership.organization_id,
        agent_id=agent.id,
        name=agent.name,
        config=agent.config,
    )

    reply_state = await outreach.execute(
        {
            "action": "check_response",
            "lead_id": str(request.lead_id),
            "has_reply": request.has_reply,
            "reply_content": request.reply_content,
            "channel": request.channel,
        },
        db,
    )

    if reply_state.get("handoff_created"):
        raise HTTPException(
            status_code=200,
            detail={
                "message": "Reply detected. Human handoff created. Automated outreach LOCKED.",
                "lead_id": str(request.lead_id),
                "handoff_created": True,
            },
        )

    return reply_state
