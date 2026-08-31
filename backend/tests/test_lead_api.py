import pytest


class TestLeadAPI:
    @pytest.mark.asyncio
    async def test_create_lead(self, auth_client):
        company_resp = await auth_client.post("/api/v1/companies/", json={
            "name": "Acme Corp",
            "domain": "acme.com",
            "industry": "technology",
            "location": "New York",
            "website": "https://acme.com",
        })
        assert company_resp.status_code == 200, company_resp.text
        company_id = company_resp.json()["id"]

        resp = await auth_client.post("/api/v1/leads/", json={
            "company_id": company_id,
            "source": "hunting",
            "source_detail": "LinkedIn",
            "source_url": "https://linkedin.com/company/acme",
            "tags": ["web-development"],
            "notes": "Decision maker found via LinkedIn",
        })
        assert resp.status_code == 200, resp.text
        lead = resp.json()
        assert lead["status"] == "new"
        assert lead["source"] == "hunting"

    @pytest.mark.asyncio
    async def test_list_leads(self, auth_client):
        resp = await auth_client.get("/api/v1/leads/")
        assert resp.status_code == 200, resp.text
        assert "leads" in resp.json()

    @pytest.mark.asyncio
    async def test_lead_handoff(self, auth_client):
        company_resp = await auth_client.post("/api/v1/companies/", json={
            "name": "Beta Inc",
            "industry": "finance",
        })
        company_id = company_resp.json()["id"]

        lead_resp = await auth_client.post("/api/v1/leads/", json={
            "company_id": company_id,
            "source": "hunting",
        })
        lead_id = lead_resp.json()["id"]

        handoff_resp = await auth_client.post(f"/api/v1/leads/{lead_id}/handoff")
        assert handoff_resp.status_code == 200, handoff_resp.text
        assert handoff_resp.json()["message"] == "Human handoff created"
