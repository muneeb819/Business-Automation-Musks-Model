from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class OrganizationCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class MembershipCreate(BaseModel):
    user_id: UUID
    role: str = "operator"
    permissions: List[str] = []


class MembershipResponse(BaseModel):
    id: UUID
    user_id: UUID
    organization_id: UUID
    role: str
    permissions: List[str]
    is_active: bool

    class Config:
        from_attributes = True
