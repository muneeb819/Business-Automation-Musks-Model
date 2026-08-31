from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.agents.base import BaseAgent
from app.models.lead import Lead
from app.models.agent import Agent, AgentStatus
from app.models.approval import Approval, ApprovalStatus
from app.models.activity import Activity
from datetime import datetime, timedelta


class SupervisorAgent(BaseAgent):
    """Control tower agent - reads, diagnoses, and recommends. Never modifies without approval."""

    def _build_system_prompt(self) -> str:
        return """You are the Supervisor Agent - the AI operations control tower.

You monitor all systems: hunting, outreach, marketing, pipeline, and health.
You answer natural-language questions about performance, failures, and status.

YOUR AUTHORITY IS DIAGNOSTIC, NOT EXECUTIVE.

You can: INSPECT, ANALYZE, DIAGNOSE, EXPLAIN, RECOMMEND
You CANNOT: modify system configuration, change settings, execute fixes

For any system modification you detect, you must:
1. Create an approval request
2. Wait for human approval
3. Only then can the fix be executed

If Muneeb gives a direct command, and it's authorized, you may execute.
For destructive actions, you require a one-line confirmation."""

    async def execute(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        action = task.get("action")

        if action == "query":
            return await self._handle_query(task, db)
        elif action == "diagnose":
            return await self._diagnose_system(task, db)
        elif action == "daily_digest":
            return await self._generate_daily_digest(task, db)
        elif action == "execute_command":
            return await self._execute_command(task, db)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def _handle_query(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        question = task.get("question", "")

        stats = {}
        result = await db.execute(
            select(func.count())
            .select_from(Lead)
            .where(Lead.organization_id == self.organization_id)
        )
        stats["total_leads"] = result.scalar()

        agents_result = await db.execute(
            select(Agent).where(Agent.organization_id == self.organization_id)
        )
        agents = agents_result.scalars().all()
        stats["active_agents"] = sum(1 for a in agents if a.status == AgentStatus.ACTIVE)
        stats["failed_agents"] = sum(1 for a in agents if a.status == AgentStatus.FAILED)
        stats["total_agents"] = len(agents)
        stats["avg_health"] = round(sum(a.health_score for a in agents) / len(agents), 1) if agents else 0

        approvals_result = await db.execute(
            select(func.count())
            .select_from(Approval)
            .where(
                Approval.organization_id == self.organization_id,
                Approval.status == ApprovalStatus.PENDING,
            )
        )
        stats["pending_approvals"] = approvals_result.scalar()

        answer = await self.generate_response(
            f"""Answer this question based on the available system data:

Question: {question}

Current system state:
- Total leads: {stats['total_leads']}
- Active agents: {stats['active_agents']}
- Failed agents: {stats['failed_agents']}
- Total agents: {stats['total_agents']}
- Average agent health: {stats['avg_health']}
- Pending approvals: {stats['pending_approvals']}

Provide a clear, data-grounded answer. If the data doesn't answer the question,
say so honestly.""",
            temperature=0.3,
        )

        return {
            "question": question,
            "answer": answer,
            "data": stats,
        }

    async def _diagnose_system(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        result = await db.execute(
            select(Agent).where(
                Agent.organization_id == self.organization_id,
                Agent.status.in_([AgentStatus.FAILED, AgentStatus.PAUSED]),
            )
        )
        problem_agents = result.scalars().all()

        diagnoses = []
        for agent in problem_agents:
            diagnosis = await self.generate_response(
                f"""Diagnose this failing agent:

Agent: {agent.name}
Type: {agent.agent_type.value}
Last error: {agent.last_error}
Health score: {agent.health_score}
Successful runs: {agent.successful_runs}
Failed runs: {agent.failed_runs}

Provide: root cause, proposed fix, expected impact, risk, rollback plan.
Format as a JSON object with those five fields.""",
                temperature=0.3,
            )
            diagnoses.append({
                "agent_id": str(agent.id),
                "agent_name": agent.name,
                "diagnosis": diagnosis,
                "needs_approval": True,
            })

        return {
            "problems_found": len(diagnoses),
            "diagnoses": diagnoses,
        }

    async def _generate_daily_digest(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        since = datetime.utcnow() - timedelta(days=1)

        leads_result = await db.execute(
            select(func.count()).select_from(Lead).where(
                Lead.organization_id == self.organization_id,
                Lead.created_at >= since,
            )
        )
        new_leads = leads_result.scalar()

        replies_result = await db.execute(
            select(func.count())
            .select_from(Activity)
            .join(Lead, Activity.lead_id == Lead.id)
            .where(
                Lead.organization_id == self.organization_id,
                Activity.action_type == "reply_received",
                Activity.created_at >= since,
            )
        )
        replies = replies_result.scalar()

        failed_result = await db.execute(
            select(func.count()).select_from(Agent).where(
                Agent.organization_id == self.organization_id,
                Agent.status == AgentStatus.FAILED,
            )
        )
        failed_agents = failed_result.scalar()

        pending_result = await db.execute(
            select(func.count()).select_from(Approval).where(
                Approval.organization_id == self.organization_id,
                Approval.status == ApprovalStatus.PENDING,
            )
        )
        pending_approvals = pending_result.scalar()

        digest = await self.generate_response(
            f"""Generate a concise daily operation digest:

- New leads discovered: {new_leads}
- Replies received: {replies}
- Failed agents: {failed_agents}
- Pending approvals: {pending_approvals}

Summarize the current health of the business development operation,
flag anything that needs attention.""",
            temperature=0.3,
        )

        return {
            "date": datetime.utcnow().isoformat(),
            "new_leads": new_leads,
            "replies": replies,
            "failed_agents": failed_agents,
            "pending_approvals": pending_approvals,
            "digest": digest,
        }

    async def _execute_command(self, task: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        command = task.get("command", "")
        is_destructive = task.get("is_destructive", False)
        confirmed = task.get("confirmed", False)

        if is_destructive and not confirmed:
            return {
                "requires_confirmation": True,
                "message": "This is a destructive action. Please confirm with 'confirmed: true'.",
                "command": command,
            }

        logger = {
            "agent": self.name,
            "action": "direct_command_executed",
            "command": command,
            "executed_at": datetime.utcnow().isoformat(),
        }

        return {
            "command": command,
            "executed": True,
            "logged": logger,
        }
