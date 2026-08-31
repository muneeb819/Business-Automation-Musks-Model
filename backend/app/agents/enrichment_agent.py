from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.base import BaseAgent
from app.services.lead_pipeline import lead_pipeline


class EnrichmentAgent(BaseAgent):
    """Enriches and verifies lead information."""

    def _build_system_prompt(self) -> str:
        return """You are a Lead Enrichment Agent.
Your job is to enrich lead data with company and contact information,
verify decision-makers, and provide confidence scores. Never represent
uncertain information as verified fact."""

    async def execute(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        lead_id = task.get("lead_id")
        if not lead_id:
            raise ValueError("lead_id is required")

        company_data = task.get("company_data", {})
        contact_data = task.get("contact_data", {})

        lead = await lead_pipeline.enrich_lead(
            lead_id=lead_id,
            company_data=company_data,
            contact_data=contact_data,
        )

        verification = task.get("verification", {})
        if verification:
            lead = await lead_pipeline.verify_lead(
                lead_id=lead_id,
                verification_data=verification,
            )

        score = task.get("scoring", {})
        if score:
            lead = await lead_pipeline.score_lead(
                lead_id=lead_id,
                fit_score=score.get("fit_score", 0),
                lead_score=score.get("lead_score", 0),
                explanation=score.get("explanation", {}),
            )

        return {
            "lead_id": str(lead_id),
            "enriched": True,
            "verified": verification.get("verified", False) if verification else False,
            "score": score.get("lead_score", 0) if score else 0,
        }
