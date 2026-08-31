from abc import ABC, abstractmethod
from typing import Any, Dict, List
from uuid import UUID


class WorkflowBackend(ABC):
    """Abstraction for durable workflow orchestration (Temporal, etc.)."""

    @abstractmethod
    async def start_workflow(self, workflow_type: str, args: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def get_workflow_status(self, workflow_id: str) -> str:
        pass

    @abstractmethod
    async def cancel_workflow(self, workflow_id: str) -> None:
        pass

    @abstractmethod
    async def signal_workflow(self, workflow_id: str, signal: str, args: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def list_workflows(self, workflow_type: str) -> List[Dict[str, Any]]:
        pass


class TemporalWorkflowBackend(WorkflowBackend):
    """Temporal implementation. Requires temporal client."""

    def __init__(self):
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            from temporalio.client import Client
            import asyncio
            self._client = asyncio.run(self._connect())
        return self._client

    async def _connect(self):
        from temporalio.client import Client
        from app.core.config import settings
        return await Client.connect(settings.TEMPORAL_HOST)

    async def start_workflow(self, workflow_type: str, args: Dict[str, Any]) -> str:
        client = self._ensure_client()
        handle = await client.start_workflow(
            workflow_type,
            args,
            id=f"{workflow_type}-{args.get('lead_id', '')}",
        )
        return handle.id

    async def get_workflow_status(self, workflow_id: str) -> str:
        client = self._ensure_client()
        handle = client.get_workflow_handle(workflow_id)
        result = await handle.result()
        return str(result)

    async def cancel_workflow(self, workflow_id: str) -> None:
        client = self._ensure_client()
        handle = client.get_workflow_handle(workflow_id)
        await handle.cancel()

    async def signal_workflow(self, workflow_id: str, signal: str, args: Dict[str, Any]) -> None:
        client = self._ensure_client()
        handle = client.get_workflow_handle(workflow_id)
        await handle.signal(signal, args)

    async def list_workflows(self, workflow_type: str) -> List[Dict[str, Any]]:
        return []


class InMemoryWorkflowBackend(WorkflowBackend):
    """In-memory implementation for development/testing."""

    def __init__(self):
        self._workflows: Dict[str, Dict[str, Any]] = {}

    async def start_workflow(self, workflow_type: str, args: Dict[str, Any]) -> str:
        import uuid
        workflow_id = str(uuid.uuid4())
        self._workflows[workflow_id] = {
            "type": workflow_type,
            "args": args,
            "status": "running",
        }
        return workflow_id

    async def get_workflow_status(self, workflow_id: str) -> str:
        if workflow_id not in self._workflows:
            raise KeyError(f"Workflow {workflow_id} not found")
        return self._workflows[workflow_id]["status"]

    async def cancel_workflow(self, workflow_id: str) -> None:
        if workflow_id in self._workflows:
            self._workflows[workflow_id]["status"] = "cancelled"

    async def signal_workflow(self, workflow_id: str, signal: str, args: Dict[str, Any]) -> None:
        if workflow_id in self._workflows:
            self._workflows[workflow_id].setdefault("signals", []).append(
                {"signal": signal, "args": args}
            )

    async def list_workflows(self, workflow_type: str) -> List[Dict[str, Any]]:
        return [
            {"id": wid, **wf}
            for wid, wf in self._workflows.items()
            if wf["type"] == workflow_type
        ]


workflow_backend: WorkflowBackend = InMemoryWorkflowBackend()
