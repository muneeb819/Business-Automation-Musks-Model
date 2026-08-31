from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from app.models.lead import Lead, LeadStatus, LeadSource
from app.models.company import Company
from app.models.contact import Contact
from app.models.activity import Activity
from app.models.campaign import Campaign
from app.core.database import async_session_factory


class LeadPipelineService:
    """Handles the lead intelligence pipeline stages."""

    @staticmethod
    async def discover_lead(
        org_id: UUID,
        company_name: str,
        source: LeadSource,
        source_detail: str = None,
        source_url: str = None,
        industry: str = None,
        website: str = None,
        metadata: dict = None,
    ) -> Lead:
        async with async_session_factory() as db:
            existing = await db.execute(
                select(Company).where(
                    Company.organization_id == org_id,
                    or_(
                        Company.name == company_name,
                        Company.domain == metadata.get("domain") if metadata else None,
                    )
                )
            )
            company = existing.scalar_one_or_none()

            if not company:
                company = Company(
                    organization_id=org_id,
                    name=company_name,
                    industry=industry,
                    website=website,
                    domain=metadata.get("domain") if metadata else None,
                )
                db.add(company)
                await db.flush()

            lead = Lead(
                organization_id=org_id,
                company_id=company.id,
                source=source,
                source_detail=source_detail,
                source_url=source_url,
                status=LeadStatus.NEW,
                meta_data=metadata or {},
            )
            db.add(lead)

            activity = Activity(
                lead_id=lead.id,
                agent_name="hunting_agent",
                action_type="lead_discovered",
                summary=f"Lead discovered from {source_detail or source.value}",
                details=metadata or {},
            )
            db.add(activity)

            await db.commit()
            return lead

    @staticmethod
    async def enrich_lead(
        lead_id: UUID,
        company_data: dict,
        contact_data: dict,
    ) -> Lead:
        async with async_session_factory() as db:
            lead = await db.get(Lead, lead_id)
            if not lead:
                raise ValueError(f"Lead {lead_id} not found")

            if lead.company_id:
                company = await db.get(Company, lead.company_id)
                if company:
                    for field, value in company_data.items():
                        setattr(company, field, value)

            contact = Contact(
                organization_id=lead.organization_id,
                company_id=lead.company_id,
                **contact_data
            )
            db.add(contact)
            await db.flush()

            lead.contact_id = contact.id
            lead.enrichment_date = datetime.utcnow()

            activity = Activity(
                lead_id=lead.id,
                agent_name="enrichment_agent",
                action_type="lead_enriched",
                summary=f"Lead enriched with contact {contact.first_name} {contact.last_name}",
            )
            db.add(activity)

            await db.commit()
            return lead

    @staticmethod
    async def verify_lead(
        lead_id: UUID,
        verification_data: dict,
    ) -> Lead:
        async with async_session_factory() as db:
            lead = await db.get(Lead, lead_id)
            if not lead:
                raise ValueError(f"Lead {lead_id} not found")

            contact = await db.get(Contact, lead.contact_id) if lead.contact_id else None
            if contact:
                contact.is_verified = verification_data.get("verified", False)
                contact.verification_status = verification_data.get("status", "unknown")
                contact.confidence_score = verification_data.get("confidence", 0)

            lead.verification_date = datetime.utcnow()
            lead.confidence_score = verification_data.get("confidence", 0)

            activity = Activity(
                lead_id=lead.id,
                agent_name="enrichment_agent",
                action_type="lead_verified",
                summary=f"Contact verified: {verification_data.get('status', 'unknown')}",
            )
            db.add(activity)

            await db.commit()
            return lead

    @staticmethod
    async def score_lead(
        lead_id: UUID,
        fit_score: float,
        lead_score: float,
        explanation: dict,
    ) -> Lead:
        async with async_session_factory() as db:
            lead = await db.get(Lead, lead_id)
            if not lead:
                raise ValueError(f"Lead {lead_id} not found")

            lead.fit_score = fit_score
            lead.lead_score = lead_score
            lead.scoring_explanation = explanation

            activity = Activity(
                lead_id=lead.id,
                agent_name="scoring_engine",
                action_type="lead_scored",
                summary=f"Lead scored: {lead_score}/100",
                details=explanation,
            )
            db.add(activity)

            await db.commit()
            return lead

    @staticmethod
    async def approve_for_outreach(lead_id: UUID) -> Lead:
        async with async_session_factory() as db:
            lead = await db.get(Lead, lead_id)
            if not lead:
                raise ValueError(f"Lead {lead_id} not found")

            lead.status = LeadStatus.NEW

            activity = Activity(
                lead_id=lead.id,
                agent_name="supervisor",
                action_type="status_change",
                summary="Lead approved for outreach",
            )
            db.add(activity)

            await db.commit()
            return lead

    @staticmethod
    async def schedule_followup(
        lead_id: UUID,
        days_offset: int,
    ) -> Lead:
        async with async_session_factory() as db:
            lead = await db.get(Lead, lead_id)
            if not lead:
                raise ValueError(f"Lead {lead_id} not found")

            lead.next_followup_date = datetime.utcnow() + timedelta(days=days_offset)

            activity = Activity(
                lead_id=lead.id,
                agent_name="outreach_agent",
                action_type="follow_up_scheduled",
                summary=f"Next follow-up scheduled in {days_offset} days",
            )
            db.add(activity)

            await db.commit()
            return lead


lead_pipeline = LeadPipelineService()
