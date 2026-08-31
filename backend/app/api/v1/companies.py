from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.core.deps import get_current_active_membership
from app.models.company import Company
from app.models.organization import Membership
from app.schemas.lead import CompanyCreate, CompanyResponse

router = APIRouter()


@router.get("/", response_model=list[CompanyResponse])
async def list_companies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    query = select(Company).where(
        Company.organization_id == membership.organization_id
    )

    if search:
        query = query.where(Company.name.ilike(f"%{search}%"))

    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Company.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Company).where(
            Company.id == company_id,
            Company.organization_id == membership.organization_id,
        )
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    company = Company(
        organization_id=membership.organization_id,
        **company_data.model_dump()
    )
    db.add(company)
    await db.flush()
    return company


@router.patch("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: UUID,
    company_data: CompanyCreate,
    membership: Membership = Depends(get_current_active_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Company).where(
            Company.id == company_id,
            Company.organization_id == membership.organization_id,
        )
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    update_data = company_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    company.updated_at = datetime.utcnow()

    return company
