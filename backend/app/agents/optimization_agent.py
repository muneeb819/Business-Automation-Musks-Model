from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.agents.base import BaseAgent
from app.models.lead import Lead, LeadStatus
from app.models.agent import Agent
from app.models.marketing import MarketingActivity
from datetime import datetime, timedelta


class OptimizationAgent(BaseAgent):
    """Business Intelligence & Optimization Agent - recommends improvements, never auto-implements."""

    def _build_system_prompt(self) -> str:
        return """You are the Business Intelligence & Optimization Agent.

You continuously study the organization to find improvement opportunities.
You analyze lead quality, conversion rates, response rates, campaign performance,
agent performance, and operational efficiency.

You RECOMMEND. You NEVER implement.
The human decides. The human approves. Only then can changes be executed."""

    async def execute(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        action = task.get("action")

        if action == "analyze":
            return await self._analyze_opportunities(task, db)
        elif action == "generate_recommendations":
            return await self._generate_recommendations(task, db)
        elif action == "simulate":
            return await self._simulate_change(task, db)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def _analyze_opportunities(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        lead_result = await db.execute(select(Lead).where(Lead.organization_id == self.organization_id))
        leads = lead_result.scalars().all()

        total = len(leads)
        contacted = sum(1 for l in leads if l.status in [LeadStatus.CONTACTED, LeadStatus.ENGAGED])
        replied = sum(1 for l in leads if l.response_date is not None)
        converted = sum(1 for l in leads if l.status == LeadStatus.CLOSED_WON)

        stats = {
            "total_leads": total,
            "contacted": contacted,
            "replied": replied,
            "converted": converted,
            "contact_rate": round((contacted / total * 100), 1) if total else 0,
            "response_rate": round((replied / contacted * 100), 1) if contacted else 0,
            "conversion_rate": round((converted / total * 100), 1) if total else 0,
        }

        opportunity = await self.generate_response(
            f"""Analyze this business development performance data and identify
the most impactful optimization opportunities:

- Total leads: {stats['total_leads']}
- Contact rate: {stats['contact_rate']}%
- Response rate: {stats['response_rate']}%
- Conversion rate: {stats['conversion_rate']}%

For each opportunity, provide: observation, hypothesis, recommended action,
expected impact, confidence, and risk.""",
            temperature=0.5,
        )

        return {
            "stats": stats,
            "opportunities": opportunity,
        }

    async def _generate_recommendations(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        analysis = task.get("analysis", {})

        recommendation = await self.generate_response(
            f"""Create a structured A/B test recommendation based on this analysis:

Statistics: {analysis}

Return the recommendation in this format:
OPPORTUNITY: [description]
OBSERVATION: [what's happening]
HYPOTHESIS: [why it's happening]
RECOMMENDATION: [what to test]
EXPECTED IMPACT: [projected improvement]
CONFIDENCE: [percentage]
RISK: [low/medium/high]
""",
            temperature=0.3,
        )

        return {
            "recommendation": recommendation,
            "requires_approval": True,
            "type": "experiment_suggestion",
        }

    async def _simulate_change(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        change = task.get("change", "")
        metric = task.get("metric", "response_rate")

        simulation = await self.generate_response(
            f"""Simulate the business impact of this operational change:

Change: {change}
Key metric affected: {metric}

Analyze historical context and estimate:
- Expected impact
- Potential downside
- Affected workflows
- Affected leads
- Expected cost
- Risk level
- Rollback requirements

Provide a conservative estimate with clear caveats.""",
            temperature=0.3,
        )

        return {
            "change": change,
            "simulation": simulation,
            "is_estimated": True,
            "requires_approval": True,
        }
