import pytest


class TestDashboardAPI:
    @pytest.mark.asyncio
    async def test_dashboard_overview(self, auth_client):
        resp = await auth_client.get("/api/v1/dashboard/overview")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "leads" in data
        assert "agents" in data
        assert "approvals" in data
        assert "notifications" in data

    @pytest.mark.asyncio
    async def test_pipeline_summary(self, auth_client):
        resp = await auth_client.get("/api/v1/dashboard/pipeline")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        for status in ["new", "contacted", "engaged", "human_handoff", "closed_won", "closed_lost"]:
            assert status in data

    @pytest.mark.asyncio
    async def test_recent_activity(self, auth_client):
        resp = await auth_client.get("/api/v1/dashboard/recent-activity")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
