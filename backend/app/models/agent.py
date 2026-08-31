import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class AgentType(enum.Enum):
    HUNTING = "hunting"
    ENRICHMENT = "enrichment"
    OUTREACH = "outreach"
    CONTENT = "content"
    SOCIAL_MEDIA = "social_media"
    SEO = "seo"
    PAID_TRAFFIC = "paid_traffic"
    ENGAGEMENT = "engagement"
    INBOUND_LEAD = "inbound_lead"
    SUPERVISOR = "supervisor"
    OPTIMIZATION = "optimization"
    MARKETPLACE = "marketplace"


class AgentStatus(enum.Enum):
    ACTIVE = "active"
    IDLE = "idle"
    PAUSED = "paused"
    FAILED = "failed"
    MAINTENANCE = "maintenance"


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    agent_type = Column(SAEnum(AgentType), nullable=False)
    status = Column(SAEnum(AgentStatus), default=AgentStatus.IDLE)
    description = Column(Text)
    config = Column(JSON, default=dict)
    tools = Column(JSON, default=list)
    permissions = Column(JSON, default=list)
    health_score = Column(Float, default=100.0)
    total_runs = Column(Integer, default=0)
    successful_runs = Column(Integer, default=0)
    failed_runs = Column(Integer, default=0)
    last_run_at = Column(DateTime)
    last_error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="agents")
    runs = relationship("AgentRun", back_populates="agent")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    status = Column(String(50), default="running")
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    duration_ms = Column(Integer)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    agent = relationship("Agent", back_populates="runs")


class AgentTool(Base):
    __tablename__ = "agent_tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    allowed_agents = Column(JSON, default=list)
    required_permissions = Column(JSON, default=list)
    input_schema = Column(JSON)
    output_schema = Column(JSON)
    risk_level = Column(String(20), default="low")
    requires_approval = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
