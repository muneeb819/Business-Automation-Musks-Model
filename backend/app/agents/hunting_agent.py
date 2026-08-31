from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.base import BaseAgent
from app.models.lead import Lead, LeadSource
from app.services.lead_pipeline import lead_pipeline


class HuntingAgent(BaseAgent):
    """Discovers leads across multiple platforms based on filters."""

    def _build_system_prompt(self) -> str:
        return """You are a Lead Discovery Agent for a business development platform.
Your job is to find high-quality leads based on organizational filters including
industry, platform, and eligibility criteria. Every lead must have validated
contact information, verified decision-makers, and be freshly posted."""

    async def execute(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        filters = task.get("filters", {})
        industries = filters.get("industries", [])
        platforms = filters.get("platforms", [])

        found_leads = []
        for lead_data in task.get("leads", []):
            lead = await lead_pipeline.discover_lead(
                org_id=self.organization_id,
                company_name=lead_data.get("company_name", ""),
                source=LeadSource.HUNTING,
                source_detail=lead_data.get("platform"),
                source_url=lead_data.get("source_url"),
                industry=lead_data.get("industry"),
                website=lead_data.get("website"),
                metadata=lead_data.get("metadata", {}),
            )
            found_leads.append({
                "lead_id": str(lead.id),
                "company_name": lead_data.get("company_name"),
                "source": lead_data.get("platform"),
            })

        return {
            "leads_found": len(found_leads),
            "leads": found_leads,
            "filters_applied": {
                "industries": industries,
                "platforms": platforms,
            }
        }
