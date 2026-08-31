import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Integration(Base):
    __tablename__ = "integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    integration_type = Column(String(100), nullable=False)
    provider = Column(String(100))
    status = Column(String(50), default="inactive")
    config = Column(JSON, default=dict)
    credentials = Column(JSON, default=dict)
    health_status = Column(String(50), default="unknown")
    last_health_check = Column(DateTime)
    error_log = Column(JSON, default=list)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("integrations.id"), nullable=True)
    url = Column(String(500), nullable=False)
    secret = Column(String(255))
    events = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime)
    failure_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
