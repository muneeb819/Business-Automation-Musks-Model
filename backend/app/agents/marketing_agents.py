from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.base import BaseAgent
from app.models.marketing import MarketingActivity
from app.models.approval import Approval, ApprovalStatus, ApprovalCategory
from datetime import datetime


class ContentAgent(BaseAgent):
    """Creates content based on approved brand/business knowledge."""

    def _build_system_prompt(self) -> str:
        return """You are a Content Marketing Agent.
Create high-quality content based on the organization's approved brand voice,
positioning, and business knowledge. All content must be approved before publication."""

    async def execute(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        content = await self.generate_response(task.get("prompt", "Create marketing content."))

        activity = MarketingActivity(
            organization_id=self.organization_id,
            agent_type="content",
            platform=task.get("platform"),
            content_type=task.get("content_type", "generic"),
            title=task.get("title"),
            content=content,
            status="pending_approval",
        )
        db.add(activity)

        approval = Approval(
            organization_id=self.organization_id,
            agent_id=self.agent_id,
            category=ApprovalCategory.MARKETING,
            title=f"Content approval: {task.get('title', 'Untitled')}",
            description="AI-generated content ready for review",
            proposed_fix=f"Publish content on {task.get('platform', 'unknown platform')}",
            affected_system="marketing",
            risk_level="low",
        )
        db.add(approval)

        await db.flush()

        return {
            "content_id": str(activity.id),
            "approval_id": str(approval.id),
            "content": content,
            "status": "pending_approval",
        }


class SocialMediaAgent(BaseAgent):
    """Prepares and publishes approved content on social platforms."""

    def _build_system_prompt(self) -> str:
        return """You are a Social Media Agent.
Prepare and, where integrations permit, publish approved content on social platforms.
Never publish without explicit approval."""

    async def execute(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        post = await self.generate_response(task.get("prompt", "Create a social media post."))

        activity = MarketingActivity(
            organization_id=self.organization_id,
            agent_type="social_media",
            platform=task.get("platform"),
            content_type="post",
            title=task.get("title"),
            content=post,
            status="pending_approval",
        )
        db.add(activity)

        approval = Approval(
            organization_id=self.organization_id,
            agent_id=self.agent_id,
            category=ApprovalCategory.MARKETING,
            title=f"Social post approval: {task.get('title', 'Untitled')}",
            description="AI-generated social media post ready for review",
            proposed_fix=f"Publish post to {task.get('platform', 'unknown platform')}",
            affected_system="marketing",
            risk_level="low",
        )
        db.add(approval)

        await db.flush()

        return {
            "post_id": str(activity.id),
            "approval_id": str(approval.id),
            "content": post,
            "status": "pending_approval",
        }


class SEOAgent(BaseAgent):
    """Analyzes search opportunities and recommends content strategies."""

    def _build_system_prompt(self) -> str:
        return """You are an SEO Agent.
Analyze search opportunities and recommend content strategies to attract relevant inbound leads."""

    async def execute(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        analysis = await self.generate_response(task.get("prompt", "Analyze SEO opportunities."))

        activity = MarketingActivity(
            organization_id=self.organization_id,
            agent_type="seo",
            platform="search",
            content_type="strategy",
            title=task.get("title"),
            content=analysis,
            status="draft",
        )
        db.add(activity)
        await db.flush()

        return {
            "analysis_id": str(activity.id),
            "content": analysis,
            "status": "draft",
        }


class PaidTrafficAgent(BaseAgent):
    """Analyzes campaign performance and recommends optimization."""

    def _build_system_prompt(self) -> str:
        return """You are a Paid Traffic Agent.
Analyze campaign performance and recommend optimizations. All spend changes require explicit approval."""

    async def execute(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        analysis = await self.generate_response(task.get("prompt", "Analyze paid campaign performance."))

        if task.get("recommend_spend_change"):
            approval = Approval(
                organization_id=self.organization_id,
                agent_id=self.agent_id,
                category=ApprovalCategory.MARKETING,
                title="Budget change approval",
                description=task.get("reason"),
                proposed_fix=analysis,
                affected_system="paid_traffic",
                risk_level="medium",
            )
            db.add(approval)
            await db.flush()

            return {
                "analysis": analysis,
                "approval_id": str(approval.id),
                "status": "pending_approval",
            }

        return {
            "analysis": analysis,
            "status": "draft",
        }


class EngagementAgent(BaseAgent):
    """Monitors engagement signals and identifies opportunities."""

    def _build_system_prompt(self) -> str:
        return """You are an Engagement Agent.
Monitor permitted engagement signals and identify opportunities for meaningful interaction."""

    async def execute(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        opportunities = await self.generate_response(task.get("prompt", "Identify engagement opportunities."))

        return {
            "opportunities": [
                {
                    "signal": opp.strip(),
                    "source": task.get("platform"),
                }
                for opp in opportunities.split("\n")
                if opp.strip()
            ],
        }
