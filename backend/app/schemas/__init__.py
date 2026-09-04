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
    ApprovalAction,
)
from app.schemas.agent import (
    AgentCreate,
    AgentResponse,
    AgentHealthScore,
    AgentRunResponse,
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
    "ApprovalAction",
    "AgentCreate",
    "AgentResponse",
    "AgentHealthScore",
    "AgentRunResponse",
    "DashboardOverview",
    "PipelineSummary",
    "RecentActivity",
    "MarketingCampaignCreate",
    "MarketingCampaignResponse",
    "OutreachProposalRequest",
    "OutreachSendRequest",
    "OutreachReplyRequest",
]
