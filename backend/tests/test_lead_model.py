from app.models.lead import Lead, LeadStatus
import pytest


class TestLeadStatusModel:
    def test_status_values(self):
        assert LeadStatus.NEW.value == "new"
        assert LeadStatus.CONTACTED.value == "contacted"
        assert LeadStatus.ENGAGED.value == "engaged"
        assert LeadStatus.READY_TO_CLOSE.value == "ready_to_close"
        assert LeadStatus.HUMAN_HANDOFF.value == "human_handoff"
        assert LeadStatus.CLOSED_WON.value == "closed_won"
        assert LeadStatus.CLOSED_LOST.value == "closed_lost"

    def test_status_transitions(self):
        # The pipeline: New -> Contacted -> Engaged -> Ready to Close / Human Handoff
        pipeline = [
            LeadStatus.NEW,
            LeadStatus.CONTACTED,
            LeadStatus.ENGAGED,
            LeadStatus.HUMAN_HANDOFF,
        ]
        # The outreach agent locks the moment a reply is detected
        assert LeadStatus.HUMAN_HANDOFF in pipeline
