from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.core.deps import get_current_active_membership, require_permission
from app.models.approval import Approval, ApprovalStatus
from app.models.organization import Membership
from app.schemas.approval import (
    ApprovalCreate,
    ApprovalResponse,
    ApprovalAction,
    ApprovalListResponse,
    ApprovalStatus as ApprovalStatusSchema,
)

router = APIRouter()


@router.get("/", response_model=ApprovalListResponse)
async def list_approvals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[ApprovalStatusSchema] = None,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    query = select(Approval).where(
        Approval.organization_id == membership.organization_id
    )

    if status:
        query = query.where(Approval.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Approval.created_at.desc())
    result = await db.execute(query)
    approvals = result.scalars().all()

    return ApprovalListResponse(
        approvals=[ApprovalResponse.model_validate(a) for a in approvals],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval(
    approval_id: UUID,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Approval).where(
            Approval.id == approval_id,
            Approval.organization_id == membership.organization_id,
        )
    )
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval


@router.post("/", response_model=ApprovalResponse)
async def create_approval(
    approval_data: ApprovalCreate,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    approval = Approval(
        organization_id=membership.organization_id,
        requester_id=membership.user_id,
        **approval_data.model_dump()
    )
    db.add(approval)
    await db.flush()
    return approval


@router.post("/{approval_id}/action", response_model=ApprovalResponse)
async def take_approval_action(
    approval_id: UUID,
    action_data: ApprovalAction,
    membership: Membership = Depends(require_permission("approvals.approve")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Approval).where(
            Approval.id == approval_id,
            Approval.organization_id == membership.organization_id,
        )
    )
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot act on approval in {approval.status} status",
        )

    if action_data.action == "approve":
        approval.status = ApprovalStatus.APPROVED
    elif action_data.action == "reject":
        approval.status = ApprovalStatus.REJECTED
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    approval.approver_id = membership.user_id
    approval.approval_notes = action_data.notes
    approval.resolved_at = datetime.utcnow()
    approval.updated_at = datetime.utcnow()

    return approval
