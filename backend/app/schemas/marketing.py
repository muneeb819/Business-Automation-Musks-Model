"""
Marketing campaign schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class MarketingCampaignCreate(BaseModel):
    """Schema for creating a marketing campaign."""
    name: str = Field(..., description="Campaign name")
    target_audience: Optional[str] = Field(None, description="Target audience description")
    messaging: Optional[str] = Field(None, description="Campaign messaging")
    channels: Optional[List[str]] = Field(default_factory=list, description="Marketing channels")
    budget: Optional[float] = Field(None, description="Marketing budget")


class MarketingCampaignResponse(BaseModel):
    """Schema for marketing campaign in responses."""
    id: UUID = Field(..., description="Campaign ID")
    name: str = Field(..., description="Campaign name")
    status: str = Field(default="active", description="Campaign status")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
