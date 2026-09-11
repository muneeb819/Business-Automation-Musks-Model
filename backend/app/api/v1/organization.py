from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_membership
from app.models.organization import Membership, Organization
from app.models.user import User

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
async def get_organization(
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    """Return the current organization and its members."""
    result = await db.execute(
        select(Organization).where(Organization.id == membership.organization_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    members_result = await db.execute(
        select(User, Membership)
        .join(Membership, Membership.user_id == User.id)
        .where(
            Membership.organization_id == org.id,
            Membership.is_active == True,  # noqa: E712
        )
        .order_by(User.full_name, User.email)
    )
    rows = members_result.all()

    members = [
        {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": membership.role,
            "is_active": bool(membership.is_active),
        }
        for user, membership in rows
    ]

    return {
        "id": str(org.id),
        "name": org.name,
        "slug": org.slug,
        "description": org.description,
        "website": org.website,
        "industry": org.industry,
        "logo_url": org.logo_url,
        "created_at": org.created_at.isoformat() if org.created_at else None,
        "members": members,
    }
