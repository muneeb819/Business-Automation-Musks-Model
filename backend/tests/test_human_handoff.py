"""
CRITICAL ACCEPTANCE TEST

The system must pass this scenario:
  Lead discovered -> enriched -> verified -> scored -> proposal generated
  -> proposal sent -> prospect replies -> AI detects reply
  -> automated outreach LOCKED -> human handoff created -> user notified
  -> human responds

The Outreach Agent must be unable to autonomously continue the conversation after a reply.
"""
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from app.models.lead import Lead, LeadStatus


class TestHumanHandoffInvariant:
    @pytest.mark.asyncio
    async def test_outreach_agent_locks_on_reply(self):
        """Verify the outreach agent transitions to HUMAN_HANDOFF on reply."""
        from app.agents.outreach_agent import OutreachAgent

        org_id = uuid4()
        agent_id = uuid4()
        lead_id = uuid4()

        agent = OutreachAgent(
            organization_id=org_id,
            agent_id=agent_id,
            name="Test Outreach Agent",
            agent_type="outreach",
        )

        mock_lead = AsyncMock()
        mock_lead.id = lead_id
        mock_lead.organization_id = org_id
        mock_lead.company_id = None
        mock_lead.company = None

        mock_db = AsyncMock()
        from unittest.mock import Mock
        result_mock = Mock()
        result_mock.scalar_one_or_none.return_value = mock_lead
        mock_db.execute.return_value = result_mock

        with patch.object(agent, "_create_notification", new=AsyncMock()):
            response = await agent._handle_handoff(
                {"lead_id": str(lead_id), "reply_content": "Hello, tell me more"},
                mock_db,
            )

        assert response["handoff_created"] is True
        assert response["outreach_locked"] is True
        assert mock_lead.status == LeadStatus.HUMAN_HANDOFF
        assert mock_lead.response_date is not None
        assert mock_lead.handoff_date is not None

    @pytest.mark.asyncio
    async def test_outreach_blocked_in_handoff_state(self):
        """Verify the outreach agent raises a permission error on send when in HUMAN_HANDOFF."""
        from app.agents.outreach_agent import OutreachAgent
        from app.models.lead import LeadStatus

        org_id = uuid4()
        agent_id = uuid4()
        lead_id = uuid4()

        agent = OutreachAgent(
            organization_id=org_id,
            agent_id=agent_id,
            name="Test Outreach Agent",
            agent_type="outreach",
        )

        mock_lead = AsyncMock()
        mock_lead.id = lead_id
        mock_lead.organization_id = org_id
        mock_lead.status = LeadStatus.HUMAN_HANDOFF

        mock_db = AsyncMock()
        from unittest.mock import Mock
        result_mock = Mock()
        result_mock.scalar_one_or_none.return_value = mock_lead
        mock_db.execute.return_value = result_mock

        with pytest.raises(PermissionError) as exc_info:
            await agent._send_outreach(
                {"lead_id": str(lead_id), "content": "Should be blocked"},
                mock_db,
            )

        assert "HUMAN_HANDOFF" in str(exc_info.value)
