from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
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


class AgentStatus(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    PAUSED = "paused"
    FAILED = "failed"
    MAINTENANCE = "maintenance"


class AgentCreate(BaseModel):
    name: str
    agent_type: AgentType
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = {}
    tools: Optional[List[str]] = []
    permissions: Optional[List[str]] = []


class AgentResponse(BaseModel):
    id: UUID
    name: str
    agent_type: AgentType
    status: AgentStatus
    health_score: float
    total_runs: int
    successful_runs: int
    failed_runs: int
    last_run_at: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class AgentHealthScore(BaseModel):
    agent_id: UUID
    agent_name: str
    availability: float
    execution_success: float
    task_completion: float
    latency: float
    error_rate: float
    output_quality: float
    cost_efficiency: float
    policy_compliance: float
    overall_score: float


class AgentRunResponse(BaseModel):
    id: UUID
    agent_id: UUID
    status: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    tokens_used: int
    cost: float
    duration_ms: Optional[int] = None
    started_at: str
    completed_at: Optional[str] = None

    class Config:
        from_attributes = True
