"""
Pydantic schemas for API request/response validation.
Organized by feature module.
"""

from app.schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    TokenRefresh,
)
from app.schemas.lead import (
    LeadCreate,
    LeadResponse,
    LeadDetailResponse,
    LeadListResponse,
    LeadUpdate,
    CompanyCreate,
    CompanyResponse,
    ContactCreate,
    ContactResponse,
)
from app.schemas.approval import (
    ApprovalCreate,
    ApprovalResponse,
    ApprovalActionRequest,
)
from app.schemas.agent import (
    AgentCreate,
    AgentResponse,
    AgentStatusUpdate,
)
from app.schemas.campaign import (
    CampaignCreate,
    CampaignResponse,
    CampaignUpdate,
)
from app.schemas.dashboard import (
    DashboardOverview,
    PipelineSummary,
    RecentActivity,
)
from app.schemas.marketing import (
    MarketingCampaignCreate,
    MarketingCampaignResponse,
)
from app.schemas.outreach import (
    OutreachProposalRequest,
    OutreachSendRequest,
    OutreachReplyRequest,
)

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "TokenRefresh",
    "LeadCreate",
    "LeadResponse",
    "LeadDetailResponse",
    "LeadListResponse",
    "LeadUpdate",
    "CompanyCreate",
    "CompanyResponse",
    "ContactCreate",
    "ContactResponse",
    "ApprovalCreate",
    "ApprovalResponse",
    "ApprovalActionRequest",
    "AgentCreate",
    "AgentResponse",
    "AgentStatusUpdate",
    "CampaignCreate",
    "CampaignResponse",
    "CampaignUpdate",
    "DashboardOverview",
    "PipelineSummary",
    "RecentActivity",
    "MarketingCampaignCreate",
    "MarketingCampaignResponse",
    "OutreachProposalRequest",
    "OutreachSendRequest",
    "OutreachReplyRequest",
]
