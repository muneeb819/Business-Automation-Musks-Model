from app.workflows.backend import InMemoryWorkflowBackend
import pytest


@pytest.mark.asyncio
class TestWorkflowBackend:
    async def test_in_memory_backend(self):
        backend = InMemoryWorkflowBackend()
        workflow_id = await backend.start_workflow(
            "test_workflow", {"lead_id": "abc"}
        )
        assert workflow_id
        status = await backend.get_workflow_status(workflow_id)
        assert status == "running"

        workflows = await backend.list_workflows("test_workflow")
        assert len(workflows) == 1
        assert workflows[0]["type"] == "test_workflow"

        await backend.cancel_workflow(workflow_id)
        status = await backend.get_workflow_status(workflow_id)
        assert status == "cancelled"

    async def test_signal_workflow(self):
        backend = InMemoryWorkflowBackend()
        workflow_id = await backend.start_workflow("signal_workflow", {})
        await backend.signal_workflow(workflow_id, "reply_detected", {"lead_id": "1"})
        wf = backend._workflows[workflow_id]
        assert wf["signals"][0]["signal"] == "reply_detected"
