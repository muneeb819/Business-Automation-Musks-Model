"""
Agent Registry - Factory pattern for creating and managing agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(
        self,
        organization_id: UUID,
        agent_id: UUID,
        name: str,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.organization_id = organization_id
        self.agent_id = agent_id
        self.name = name
        self.config = config or {}

    @abstractmethod
    async def execute(self, payload: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Execute agent action with given payload."""
        pass


class OutreachAgent(BaseAgent):
    """Agent for handling outreach activities."""

    async def execute(self, payload: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Execute outreach action."""
        action = payload.get("action")
        lead_id = payload.get("lead_id")
        content = payload.get("content")

        logger.info(f"Outreach Agent executing action: {action} for lead: {lead_id}")

        if action == "generate_proposal":
            return {
                "status": "success",
                "message": "Proposal generated",
                "lead_id": lead_id,
            }
        elif action == "send_outreach":
            return {
                "status": "success",
                "message": "Outreach sent",
                "lead_id": lead_id,
                "channel": payload.get("channel", "email"),
            }
        elif action == "check_response":
            has_reply = payload.get("has_reply", False)
            if has_reply:
                return {
                    "status": "success",
                    "message": "Reply detected. Lead handoff created.",
                    "lead_id": lead_id,
                    "handoff_created": True,
                }
            return {"status": "success", "lead_id": lead_id, "handoff_created": False}
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}


class MarketingAgent(BaseAgent):
    """Agent for handling marketing activities."""

    async def execute(self, payload: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Execute marketing action."""
        action = payload.get("action")
        logger.info(f"Marketing Agent executing action: {action}")
        return {"status": "success", "message": f"Marketing action executed: {action}"}


class AnalyticsAgent(BaseAgent):
    """Agent for handling analytics and reporting."""

    async def execute(self, payload: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Execute analytics action."""
        action = payload.get("action")
        logger.info(f"Analytics Agent executing action: {action}")
        return {"status": "success", "message": f"Analytics action executed: {action}"}


class AgentRegistry:
    """Registry for creating and managing agents."""

    _agents: Dict[str, type] = {
        "outreach": OutreachAgent,
        "marketing": MarketingAgent,
        "analytics": AnalyticsAgent,
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
                f"Unknown agent type: {agent_type}. Available types: {list(cls._agents.keys())}"
            )

        agent_class = cls._agents[agent_type]
        return agent_class(
            organization_id=organization_id,
            agent_id=agent_id,
            name=name,
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
