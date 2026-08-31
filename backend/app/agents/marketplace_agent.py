from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.agents.base import BaseAgent
from app.models.approval import Approval, ApprovalStatus, ApprovalCategory
from app.models.lead import Lead, LeadSource


class MarketplaceAgent(BaseAgent):
    """Detects buyer/renter demand and surfaces for approval. No outreach without approval."""

    def _build_system_prompt(self) -> str:
        return """You are a Marketplace Demand-Detection Agent.

Your job is to detect buyer/renter intent leads on classifieds and resale platforms
(OLX, Facebook Marketplace, etc.) for goods, vehicles, property, or any category.

CRITICAL RULE:
You surface demand to the human. You NEVER send offers or outreach autonomously.
Every fulfillment action requires Muneeb's explicit approval."""

    async def execute(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        action = task.get("action")

        if action == "detect_demand":
            return await self._detect_demand(task, db)
        elif action == "surface_for_approval":
            return await self._surface_for_approval(task, db)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def _detect_demand(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        demands = task.get("demands", [])

        detected = []
        for demand in demands:
            detected.append({
                "category": demand.get("category"),
                "description": demand.get("description"),
                "budget": demand.get("budget"),
                "location": demand.get("location"),
                "platform": demand.get("platform"),
                "source_url": demand.get("source_url"),
            })

        return {
            "demands_detected": len(detected),
            "demands": detected,
            "requires_approval": True,
        }

    async def _surface_for_approval(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        demand = task.get("demand", {})

        lead = Lead(
            organization_id=self.organization_id,
            source=LeadSource.MARKETPLACE,
            source_detail=demand.get("platform"),
            source_url=demand.get("source_url"),
            meta_data={
                "category": demand.get("category"),
                "description": demand.get("description"),
                "budget": demand.get("budget"),
                "location": demand.get("location"),
            },
            personalization_data={"budget": demand.get("budget"), "category": demand.get("category")},
        )
        db.add(lead)
        await db.flush()

        approval = Approval(
            organization_id=self.organization_id,
            agent_id=self.agent_id,
            category=ApprovalCategory.OUTREACH,
            title=f"Offer to fulfill demand: {demand.get('category', 'Unknown')}",
            description=demand.get("description", ""),
            proposed_fix=f"Send fulfillment offer for budget {demand.get('budget', 'N/A')}",
            affected_system="marketplace",
            risk_level="medium",
        )
        db.add(approval)
        await db.flush()

        return {
            "lead_id": str(lead.id),
            "approval_id": str(approval.id),
            "message": "Demand surfaced. No outreach sent - awaiting Muneeb's approval.",
            "status": "awaiting_approval",
        }
