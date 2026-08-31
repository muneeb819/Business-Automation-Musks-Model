import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class MarketingAgentType(enum.Enum):
    CONTENT = "content"
    SOCIAL_MEDIA = "social_media"
    SEO = "seo"
    PAID_TRAFFIC = "paid_traffic"
    ENGAGEMENT = "engagement"


class MarketingActivity(Base):
    __tablename__ = "marketing_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    agent_type = Column(SAEnum(MarketingAgentType), nullable=False)
    platform = Column(String(100))
    content_type = Column(String(50))
    title = Column(String(500))
    content = Column(String)
    publish_date = Column(DateTime)
    views = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    clicks = Column(Integer, default=0)
    leads_attributed = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    cost_per_lead = Column(Float)
    status = Column(String(50), default="draft")
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String)
    experiment_type = Column(String(50))
    status = Column(String(50), default="draft")
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    metric = Column(String(100))
    result = Column(String)
    confidence = Column(Float)
    decision = Column(String)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    variants = relationship("ExperimentVariant", back_populates="experiment")


class ExperimentVariant(Base):
    __tablename__ = "experiment_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiments.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String)
    population = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    meta_data = Column(JSON, default=dict)

    experiment = relationship("Experiment", back_populates="variants")
