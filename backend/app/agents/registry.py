from typing import Dict, Optional
from uuid import UUID
from app.agents.base import BaseAgent
from app.agents.hunting_agent import HuntingAgent
from app.agents.enrichment_agent import EnrichmentAgent
from app.agents.outreach_agent import OutreachAgent
from app.agents.supervisor_agent import SupervisorAgent
from app.agents.optimization_agent import OptimizationAgent
from app.agents.marketplace_agent import MarketplaceAgent


class AgentRegistry:
    """Registry for creating and managing agent instances."""

    _agents: Dict[str, type] = {}

    @classmethod
    def register(cls, agent_type: str, agent_class: type):
        cls._agents[agent_type] = agent_class

    @classmethod
    def create(
        cls,
        agent_type: str,
        organization_id: UUID,
        agent_id: UUID,
        name: str,
        config: Optional[dict] = None,
    ) -> BaseAgent:
        agent_class = cls._agents.get(agent_type)
        if agent_class is None:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return agent_class(
            organization_id=organization_id,
            agent_id=agent_id,
            name=name,
            agent_type=agent_type,
            config=config,
        )


AgentRegistry.register("hunting", HuntingAgent)
AgentRegistry.register("enrichment", EnrichmentAgent)
AgentRegistry.register("outreach", OutreachAgent)
AgentRegistry.register("supervisor", SupervisorAgent)
AgentRegistry.register("optimization", OptimizationAgent)
AgentRegistry.register("marketplace", MarketplaceAgent)
