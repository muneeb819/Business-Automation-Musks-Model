from typing import Dict, Any
from app.workflows.backend import workflow_backend


class WorkflowService:
    """Service layer for orchestrating workflow execution."""

    @staticmethod
    async def start_lead_discovery(org_id: str, filters: Dict[str, Any]) -> str:
        return await workflow_backend.start_workflow(
            "lead_discovery_workflow",
            {"organization_id": org_id, "filters": filters},
        )

    @staticmethod
    async def start_outreach_campaign(org_id: str, lead_id: str, proposal: str) -> str:
        return await workflow_backend.start_workflow(
            "outreach_workflow",
            {"organization_id": org_id, "lead_id": lead_id, "proposal": proposal},
        )

    @staticmethod
    async def start_outreach_lifecycle(org_id: str, lead_id: str) -> str:
        return await workflow_backend.start_workflow(
            "outreach_lifecycle",
            {"organization_id": org_id, "lead_id": lead_id},
        )

    @staticmethod
    async def start_daily_digest(org_id: str) -> str:
        return await workflow_backend.start_workflow(
            "daily_digest",
            {"organization_id": org_id},
        )

    @staticmethod
    async def signal_reply_detected(workflow_id: str, reply: Dict[str, Any]) -> None:
        await workflow_backend.signal_workflow(workflow_id, "reply_detected", reply)

    @staticmethod
    async def get_status(workflow_id: str) -> str:
        return await workflow_backend.get_workflow_status(workflow_id)

    @staticmethod
    async def cancel(workflow_id: str) -> None:
        await workflow_backend.cancel_workflow(workflow_id)


workflow_service = WorkflowService()
