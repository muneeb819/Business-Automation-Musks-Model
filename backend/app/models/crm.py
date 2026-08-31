import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class LeadStatus(enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    DISQUALIFIED = "disqualified"
    READY_TO_CLOSE = "ready_to_close"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    HUMAN_HANDOFF = "human_handoff"


class LeadSource(enum.Enum):
    HUNTING = "hunting"
    LINKEDIN_ORGANIC = "linkedin_organic"
    PAID_AD = "paid_ad"
    SEO = "seo"
    REFERRAL = "referral"
    INBOUND_FORM = "inbound_form"
    MANUAL_IMPORT = "manual_import"
    MARKETPLACE = "marketplace"


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), index=True)
    industry = Column(String(255))
    location = Column(String(255))
    country = Column(String(100))
    size = Column(String(50))
    employee_count = Column(Integer)
    revenue_range = Column(String(100))
    description = Column(Text)
    website = Column(String(500))
    linkedin_url = Column(String(500))
    logo_url = Column(String(500))
    tech_stack = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    meta_data = Column(JSON, default=dict)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="companies")
    contacts = relationship("Contact", back_populates="company")
    leads = relationship("Lead", back_populates="company")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    title = Column(String(255))
    email = Column(String(255), index=True)
    phone = Column(String(50))
    linkedin_url = Column(String(500))
    is_decision_maker = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    verification_status = Column(String(50))
    confidence_score = Column(Float)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="contacts")
    company = relationship("Company", back_populates="contacts")
    leads = relationship("Lead", back_populates="contact")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)

    source = Column(SAEnum(LeadSource), nullable=False)
    source_detail = Column(String(500))
    source_url = Column(String(500))

    status = Column(SAEnum(LeadStatus), default=LeadStatus.NEW, nullable=False)
    fit_score = Column(Float, default=0)
    lead_score = Column(Float, default=0)
    intent_score = Column(Float, default=0)
    confidence_score = Column(Float, default=0)

    assigned_agent = Column(String(255))
    assigned_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    discovery_date = Column(DateTime, default=datetime.utcnow)
    enrichment_date = Column(DateTime)
    verification_date = Column(DateTime)
    first_contact_date = Column(DateTime)
    last_activity_date = Column(DateTime)
    response_date = Column(DateTime)
    handoff_date = Column(DateTime)
    close_date = Column(DateTime)

    outreach_count = Column(Integer, default=0)
    last_outreach_date = Column(DateTime)
    next_followup_date = Column(DateTime)

    personalization_data = Column(JSON, default=dict)
    scoring_explanation = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    notes = Column(Text)
    meta_data = Column(JSON, default=dict)

    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="leads")
    company = relationship("Company", back_populates="leads")
    contact = relationship("Contact", back_populates="leads")
    campaign = relationship("Campaign", back_populates="leads")
    activities = relationship("Activity", back_populates="lead")
    outreach_messages = relationship("OutreachMessage", back_populates="lead")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    campaign_type = Column(String(50))
    status = Column(String(50), default="active")
    target_industries = Column(JSON, default=list)
    target_platforms = Column(JSON, default=list)
    messaging_template = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget = Column(Float)
    spend = Column(Float, default=0)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="campaigns")
    leads = relationship("Lead", back_populates="campaign")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    agent_name = Column(String(255))
    action_type = Column(String(50), nullable=False)
    channel = Column(String(50))
    summary = Column(Text)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="activities")


class OutreachMessage(Base):
    __tablename__ = "outreach_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    channel = Column(String(50), nullable=False)
    subject = Column(String(500))
    content = Column(Text, nullable=False)
    status = Column(String(50), default="draft")
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    opened_at = Column(DateTime)
    replied_at = Column(DateTime)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="outreach_messages")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    channel = Column(String(50), nullable=False)
    status = Column(String(50), default="active")
    started_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime)
    meta_data = Column(JSON, default=dict)

    messages = relationship("ConversationMessage", back_populates="conversation")


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    sender_type = Column(String(50), nullable=False)
    sender_id = Column(UUID(as_uuid=True))
    content = Column(Text, nullable=False)
    channel = Column(String(50))
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
