from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.deps import get_current_active_membership
from app.models.organization import Membership
from app.models.agent import Agent, AgentType
from app.models.lead import Lead, LeadStatus
from app.agents.registry import AgentRegistry
import logging

logger = logging.getLogger(__name__)

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
    """Generate an outreach proposal for a lead."""
    try:
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

        result = await outreach.execute(
            {"action": "generate_proposal", "lead_id": str(request.lead_id)},
            db,
        )
        return result
    except Exception as e:
        logger.error(f"Error generating proposal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate proposal",
        )


@router.post("/send")
async def send_outreach(
    request: SendOutreachRequest,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    """Send an outreach message to a lead."""
    try:
        # Check if lead has already been handed off
        lead_result = await db.execute(
            select(Lead).where(
                Lead.id == request.lead_id,
                Lead.organization_id == membership.organization_id,
            )
        )
        lead = lead_result.scalar_one_or_none()

        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found",
            )

        if lead.status == LeadStatus.HUMAN_HANDOFF:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Lead has been handed off to human. Automated outreach is LOCKED.",
            )

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

        result = await outreach.execute(
            {
                "action": "send_outreach",
                "lead_id": str(request.lead_id),
                "content": request.content,
                "channel": request.channel,
            },
            db,
        )

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending outreach: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send outreach",
        )


@router.post("/check-reply")
async def check_reply(
    request: CheckReplyRequest,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    """Check if a lead has replied and handle handoff if needed.

    KEY INVARIANT: When a prospect replies, the lead is immediately set to
    HUMAN_HANDOFF and the agent is locked out. No further automated actions allowed.
    """
    try:
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

        # If reply was detected, lock the lead for human handoff
        if reply_state.get("handoff_created"):
            lead_result = await db.execute(
                select(Lead).where(
                    Lead.id == request.lead_id,
                    Lead.organization_id == membership.organization_id,
                )
            )
            lead = lead_result.scalar_one_or_none()

            if lead:
                # CRITICAL: Set lead to HUMAN_HANDOFF - HARD LOCK
                lead.status = LeadStatus.HUMAN_HANDOFF
                lead.response_date = datetime.now(timezone.utc)
                lead.handoff_date = datetime.now(timezone.utc)
                lead.assigned_user_id = membership.user_id
                lead.updated_at = datetime.now(timezone.utc)
                await db.flush()
                logger.info(
                    f"Lead {request.lead_id} set to HUMAN_HANDOFF - Outreach Agent LOCKED"
                )

            # Return success response (not error)
            return {
                "status": "success",
                "message": "Reply detected. Human handoff created. Automated outreach LOCKED.",
                "lead_id": str(request.lead_id),
                "handoff_created": True,
            }

        return reply_state
    except Exception as e:
        logger.error(f"Error checking reply: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check reply",
        )
