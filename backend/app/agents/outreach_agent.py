from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.agents.base import BaseAgent
from app.models.lead import Lead, LeadStatus
from app.models.company import Company
from app.models.activity import Activity
from app.models.approval import Approval, ApprovalStatus, ApprovalCategory
from app.models.outreach import OutreachMessage
from uuid import UUID


class OutreachAgent(BaseAgent):
    """Handles personalized outreach with strict human-handoff rules."""

    def _build_system_prompt(self) -> str:
        return """You are an Outreach Agent for a business development platform.

Your responsibilities:
1. Receive approved leads
2. Understand company context
3. Understand the organization's service offering
4. Retrieve relevant business knowledge
5. Generate personalized outreach
6. Select an authorized channel
7. Send the message
8. Record the action
9. Monitor for a response

CRITICAL RULES:
- Never falsely claim relationships that don't exist
- Never falsely claim results that aren't verified
- Never claim credentials that don't exist
- Never use case studies that aren't real
- Never make guarantees
- Personalization must be evidence-based
- The moment a prospect replies, you MUST STOP. A human takes over."""

    async def execute(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        action = task.get("action")

        if action == "generate_proposal":
            return await self._generate_proposal(task, db)
        elif action == "send_outreach":
            return await self._send_outreach(task, db)
        elif action == "check_response":
            return await self._check_response(task, db)
        elif action == "handle_handoff":
            return await self._handle_handoff(task, db)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def _generate_proposal(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        lead_id = UUID(task.get("lead_id"))
        result = await db.execute(select(Lead).where(Lead.id == lead_id))
        lead = result.scalar_one_or_none()

        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        company = None
        if lead.company_id:
            company_result = await db.execute(select(Company).where(Company.id == lead.company_id))
            company = company_result.scalar_one_or_none()

        proposal = await self.generate_response(
            f"""Generate a personalized outreach proposal for this lead:

Company: {company.name if company else 'Unknown'}
Industry: {company.industry if company else 'Unknown'}
Location: {company.location if company else 'Unknown'}
Contact context: {lead.personalization_data}

The proposal should be:
- Concise and professional
- Evidence-based personalization
- Focused on value for the prospect
- Free of any false claims or guarantees
- Under 150 words""",
            temperature=0.7,
        )

        return {
            "lead_id": str(lead_id),
            "proposal": proposal,
            "needs_approval": True,
        }

    async def _send_outreach(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        lead_id = UUID(task.get("lead_id"))
        content = task.get("content")
        channel = task.get("channel", "email")

        result = await db.execute(select(Lead).where(Lead.id == lead_id))
        lead = result.scalar_one_or_none()

        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        if lead.status == LeadStatus.HUMAN_HANDOFF:
            raise PermissionError("Cannot send automated outreach to lead in HUMAN_HANDOFF status")

        message = OutreachMessage(
            lead_id=lead.id,
            organization_id=lead.organization_id,
            channel=channel,
            content=content,
            status="sent",
            sent_at=datetime.utcnow(),
        )
        db.add(message)

        lead.outreach_count += 1
        lead.last_outreach_date = datetime.utcnow()
        if lead.status == LeadStatus.NEW:
            lead.status = LeadStatus.CONTACTED
        lead.last_activity_date = datetime.utcnow()

        activity = Activity(
            lead_id=lead.id,
            agent_name=self.name,
            action_type="outreach_sent",
            channel=channel,
            summary=f"Outreach #{lead.outreach_count} sent via {channel}",
        )
        db.add(activity)

        import asyncio
        await db.flush()

        return {
            "lead_id": str(lead_id),
            "message_id": str(message.id),
            "outreach_count": lead.outreach_count,
            "channel": channel,
            "sent": True,
        }

    async def _check_response(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        lead_id = UUID(task.get("lead_id"))

        result = await db.execute(select(Lead).where(Lead.id == lead_id))
        lead = result.scalar_one_or_none()

        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        has_reply = task.get("has_reply", False)

        if has_reply:
            return await self._handle_handoff({
                "lead_id": str(lead_id),
                "reply_content": task.get("reply_content"),
                "channel": task.get("channel"),
            }, db)

        return {
            "lead_id": str(lead_id),
            "has_reply": False,
            "status": lead.status.value,
        }

    async def _handle_handoff(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        lead_id = UUID(task.get("lead_id"))

        result = await db.execute(select(Lead).where(Lead.id == lead_id))
        lead = result.scalar_one_or_none()

        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        lead.status = LeadStatus.HUMAN_HANDOFF
        lead.response_date = datetime.utcnow()
        lead.handoff_date = datetime.utcnow()
        lead.last_activity_date = datetime.utcnow()

        activity = Activity(
            lead_id=lead.id,
            agent_name=self.name,
            action_type="reply_received",
            channel=task.get("channel"),
            summary="Reply detected - automated outreach locked, human handoff created",
            details={"reply_content": task.get("reply_content")},
        )
        db.add(activity)

        notification = await self._create_notification(lead, db)

        await db.flush()

        return {
            "lead_id": str(lead_id),
            "handoff_created": True,
            "outreach_locked": True,
            "message": "Human handoff created. Automated outreach is now locked.",
        }

    async def _create_notification(self, lead: Lead, db: AsyncSession) -> None:
        from app.models.notification import Notification, NotificationType

        notification = Notification(
            organization_id=lead.organization_id,
            type=NotificationType.HUMAN_HANDOFF,
            reference_id=lead.id,
            reference_type="lead",
            title="Human handoff required",
            message="A prospect has replied. Please take over the conversation.",
        )
        db.add(notification)
