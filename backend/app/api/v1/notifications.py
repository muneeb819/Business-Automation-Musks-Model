from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_active_membership
from app.models.notification import Notification
from app.models.organization import Membership

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def _serialize(n: Notification) -> dict:
    return {
        "id": str(n.id),
        "type": n.type.value if hasattr(n.type, "value") else str(n.type),
        "reference_type": n.reference_type,
        "title": n.title,
        "message": n.message,
        "channel": n.channel.value if hasattr(n.channel, "value") else (n.channel or "dashboard"),
        "is_read": bool(n.is_read),
        "sent_at": n.sent_at.isoformat() if n.sent_at else None,
    }


@router.get("")
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    """List notifications for the current organization with unread count."""
    org_id = membership.organization_id

    base_query = select(Notification).where(Notification.organization_id == org_id)

    total_result = await db.execute(
        select(func.count()).select_from(Notification).where(
            Notification.organization_id == org_id
        )
    )
    total = total_result.scalar() or 0

    unread_result = await db.execute(
        select(func.count()).select_from(Notification).where(
            Notification.organization_id == org_id,
            Notification.is_read == False,  # noqa: E712
        )
    )
    unread = unread_result.scalar() or 0

    result = await db.execute(
        base_query.order_by(Notification.sent_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    notifications = result.scalars().all()

    return {
        "notifications": [_serialize(n) for n in notifications],
        "unread": unread,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    """Mark a single notification as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.organization_id == membership.organization_id,
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    notification.read_at = datetime.utcnow()
    await db.flush()

    return {
        "message": "Notification marked as read",
        "notification_id": str(notification_id),
    }


@router.post("/read-all")
async def mark_all_notifications_read(
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications in the organization as read."""
    from sqlalchemy import update

    result = await db.execute(
        update(Notification)
        .where(
            Notification.organization_id == membership.organization_id,
            Notification.is_read == False,  # noqa: E712
        )
        .values(is_read=True, read_at=datetime.utcnow())
    )
    await db.flush()

    updated = result.rowcount or 0
    return {
        "message": f"Marked {updated} notifications as read",
        "updated": updated,
    }
