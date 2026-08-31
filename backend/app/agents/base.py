from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_factory
from app.models.agent import Agent, AgentRun
from app.services.ai import ai_service
from datetime import datetime


class BaseAgent(ABC):
    """Base class for all AI agents."""

    def __init__(
        self,
        organization_id: UUID,
        agent_id: UUID,
        name: str,
        agent_type: str,
        config: Optional[Dict] = None,
    ):
        self.organization_id = organization_id
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.config = config or {}
        self.system_prompt = self._build_system_prompt()

    @abstractmethod
    def _build_system_prompt(self) -> str:
        pass

    @abstractmethod
    async def execute(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        pass

    async def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        async with async_session_factory() as db:
            run = AgentRun(
                agent_id=self.agent_id,
                organization_id=self.organization_id,
                status="running",
                input_data=task,
            )
            db.add(run)
            await db.flush()

            try:
                import time
                start = time.monotonic()
                result = await self.execute(task, db)
                duration = int((time.monotonic() - start) * 1000)

                run.status = "completed"
                run.output_data = result
                run.duration_ms = duration

                agent = await db.get(Agent, self.agent_id)
                if agent:
                    agent.total_runs += 1
                    agent.successful_runs += 1
                    agent.last_run_at = datetime.utcnow()

                await db.commit()
                return result

            except Exception as e:
                run.status = "failed"
                run.error_message = str(e)

                agent = await db.get(Agent, self.agent_id)
                if agent:
                    agent.total_runs += 1
                    agent.failed_runs += 1
                    agent.last_error = str(e)

                await db.commit()
                raise

    async def generate_response(self, prompt: str, temperature: float = 0.7) -> str:
        return await ai_service.generate(
            [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
