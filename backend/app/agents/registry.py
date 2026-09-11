"""
Agent Registry - Factory pattern for creating and managing agents.

This registry maps an agent type string to the real agent implementation so
that API endpoints (outreach, supervisor, optimization, marketplace, ...) can
instantiate the correct agent with full behaviour (persistence, hard-lock
invariants, AI-backed responses) instead of mock stubs.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import BaseAgent
from app.agents.outreach_agent import OutreachAgent
from app.agents.supervisor_agent import SupervisorAgent
from app.agents.optimization_agent import OptimizationAgent
from app.agents.marketplace_agent import MarketplaceAgent
from app.agents.hunting_agent import HuntingAgent
from app.agents.enrichment_agent import EnrichmentAgent
from app.agents.marketing_agents import (
    ContentAgent,
    SocialMediaAgent,
    SEOAgent,
    PaidTrafficAgent,
    EngagementAgent,
)

import logging

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry for creating and managing agents."""

    _agents: Dict[str, type] = {
        "outreach": OutreachAgent,
        "supervisor": SupervisorAgent,
        "optimization": OptimizationAgent,
        "marketplace": MarketplaceAgent,
        "hunting": HuntingAgent,
        "enrichment": EnrichmentAgent,
        "content": ContentAgent,
        "social_media": SocialMediaAgent,
        "seo": SEOAgent,
        "paid_traffic": PaidTrafficAgent,
        "engagement": EngagementAgent,
    }

    @classmethod
    def create(
        cls,
        agent_type: str,
        organization_id: UUID,
        agent_id: UUID,
        name: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> BaseAgent:
        """Create an agent instance by type.

        Args:
            agent_type: Type of agent to create
            organization_id: Organization ID
            agent_id: Agent ID
            name: Agent name
            config: Optional agent configuration

        Returns:
            Agent instance

        Raises:
            ValueError: If agent type is unknown
        """
        if agent_type not in cls._agents:
            raise ValueError(
                f"Unknown agent type: {agent_type}. "
                f"Available types: {list(cls._agents.keys())}"
            )

        agent_class = cls._agents[agent_type]
        return agent_class(
            organization_id=organization_id,
            agent_id=agent_id,
            name=name,
            agent_type=agent_type,
            config=config,
        )

    @classmethod
    def register(cls, agent_type: str, agent_class: type) -> None:
        """Register a new agent type.

        Args:
            agent_type: Unique agent type identifier
            agent_class: Agent class (must inherit from BaseAgent)
        """
        if not issubclass(agent_class, BaseAgent):
            raise TypeError(f"Agent class must inherit from BaseAgent")
        cls._agents[agent_type] = agent_class
        logger.info(f"Registered agent type: {agent_type}")

    @classmethod
    def get_available_types(cls) -> list:
        """Get list of available agent types."""
        return list(cls._agents.keys())
