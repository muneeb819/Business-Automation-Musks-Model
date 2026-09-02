"""
Dashboard schemas for analytics and reporting.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class MetricData(BaseModel):
    """Schema for metric data points."""
    label: str = Field(..., description="Metric label")
    value: float = Field(..., description="Metric value")


class DashboardOverview(BaseModel):
    """Schema for dashboard overview data."""
    total_leads: int = Field(..., description="Total number of leads")
    total_companies: int = Field(..., description="Total number of companies")
    active_campaigns: int = Field(..., description="Number of active campaigns")
    conversion_rate: float = Field(..., description="Overall conversion rate")
    avg_lead_score: float = Field(..., description="Average lead score")
    metrics: List[MetricData] = Field(default_factory=list, description="Additional metrics")


class PipelineSummary(BaseModel):
    """Schema for sales pipeline summary."""
    new_leads: int = Field(..., description="Leads in NEW status")
    contacted: int = Field(..., description="Leads in CONTACTED status")
    engaged: int = Field(..., description="Leads in ENGAGED status")
    ready_to_close: int = Field(..., description="Leads ready to close")
    closed_won: int = Field(..., description="Won deals")
    closed_lost: int = Field(..., description="Lost deals")
    human_handoff: int = Field(..., description="Leads handed off to humans")


class ActivityItem(BaseModel):
    """Schema for a single activity item."""
    id: str = Field(..., description="Activity ID")
    type: str = Field(..., description="Activity type")
    description: str = Field(..., description="Activity description")
    timestamp: datetime = Field(..., description="When activity occurred")
    lead_id: Optional[str] = Field(None, description="Associated lead ID")


class RecentActivity(BaseModel):
    """Schema for recent activity list."""
    activities: List[ActivityItem] = Field(..., description="List of recent activities")
    total: int = Field(..., description="Total activities available")
