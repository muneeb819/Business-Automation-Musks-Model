from typing import Any, Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    campaign_type: Optional[str] = None
    status: Optional[str] = "active"
    target_industries: Optional[List[str]] = None
    target_platforms: Optional[List[str]] = None
    messaging_template: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    meta_data: Optional[Dict[str, Any]] = None


class CampaignUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = None
    description: Optional[str] = None
    campaign_type: Optional[str] = None
    status: Optional[str] = None
    target_industries: Optional[List[str]] = None
    target_platforms: Optional[List[str]] = None
    messaging_template: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    spend: Optional[float] = None
    meta_data: Optional[Dict[str, Any]] = None
