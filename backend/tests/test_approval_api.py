import pytest


class TestApprovalAPI:
    @pytest.mark.asyncio
    async def test_create_approval(self, auth_client):
        resp = await auth_client.post("/api/v1/approvals/", json={
            "category": "bug_fix",
            "title": "Fix outreach template typo",
            "description": "Found a typo in the outreach email template",
            "proposed_fix": "Update the template text",
            "affected_system": "outreach",
            "risk_level": "low",
        })
        assert resp.status_code == 200, resp.text
        approval = resp.json()
        assert approval["status"] == "pending"
        assert approval["category"] == "bug_fix"

    @pytest.mark.asyncio
    async def test_list_pending_approvals(self, auth_client):
        resp = await auth_client.get("/api/v1/approvals/")
        assert resp.status_code == 200
        assert "approvals" in resp.json()

    @pytest.mark.asyncio
    async def test_approve_approval(self, auth_client):
        create_resp = await auth_client.post("/api/v1/approvals/", json={
            "category": "ui_ux",
            "title": "Improve dashboard layout",
            "description": "Dashboard layout could be more responsive",
            "proposed_fix": "Adjust CSS breakpoints",
            "affected_system": "dashboard",
            "risk_level": "medium",
        })
        approval_id = create_resp.json()["id"]

        action_resp = await auth_client.post(
            f"/api/v1/approvals/{approval_id}/action",
            json={"action": "approve", "notes": "Looks good"},
        )
        assert action_resp.status_code == 200, action_resp.text
        assert action_resp.json()["status"] == "approved"

    @pytest.mark.asyncio
    async def test_reject_approval(self, auth_client):
        create_resp = await auth_client.post("/api/v1/approvals/", json={
            "category": "other",
            "title": "Reject this",
            "description": "Not needed",
            "proposed_fix": "None",
            "risk_level": "low",
        })
        approval_id = create_resp.json()["id"]

        action_resp = await auth_client.post(
            f"/api/v1/approvals/{approval_id}/action",
            json={"action": "reject", "notes": "Not needed"},
        )
        assert action_resp.status_code == 200
        assert action_resp.json()["status"] == "rejected"
