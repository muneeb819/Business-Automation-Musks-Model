from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from uuid import UUID
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.deps import get_current_user
from app.models.user import User
from app.models.organization import Membership, Organization
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    TokenResponse,
    TokenRefresh,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


async def _extract_credentials(request: Request):
    """Extract (email, password) from either a JSON or form-encoded body.

    The frontend sends ``application/x-www-form-urlencoded`` (OAuth2 style,
    with ``username``/``password`` fields), while API clients may send a JSON
    body with ``email``/``password``. Both are supported.
    """
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid JSON body",
            )
        email = body.get("email")
        password = body.get("password")
    else:
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="email and password are required",
        )
    return str(email), str(password)


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user and create their organization."""
    try:
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
        )
        db.add(user)
        await db.flush()
        logger.info(f"Created new user: {user.email}")

        org = Organization(
            name=f"{user_data.full_name}'s Organization",
            slug=user_data.email.split("@")[0],
        )
        db.add(org)
        await db.flush()
        logger.info(f"Created new organization: {org.id}")

        membership = Membership(
            user_id=user.id,
            organization_id=org.id,
            role="owner",
            permissions=[
                "leads.read",
                "leads.write",
                "leads.delete",
                "companies.read",
                "companies.write",
                "companies.delete",
                "contacts.read",
                "contacts.write",
                "contacts.delete",
                "campaigns.read",
                "campaigns.write",
                "campaigns.delete",
                "agents.read",
                "agents.write",
                "agents.delete",
                "approvals.read",
                "approvals.write",
                "approvals.approve",
                "settings.read",
                "settings.write",
                "audit.read",
                "users.read",
                "users.write",
            ],
        )
        db.add(membership)
        await db.flush()
        logger.info(f"Created membership for user: {user.id}")

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return tokens.

    Accepts both JSON (``{"email": ..., "password": ...}``) and
    form-encoded (``username``/``password``) request bodies.
    """
    email, password = await _extract_credentials(request)
    try:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        logger.info(f"User logged in: {user.email}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to authenticate",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    try:
        payload = decode_token(token_data.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        user_id = payload.get("sub")
        try:
            user_uuid = UUID(str(user_id))
        except (ValueError, TypeError, AttributeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        result = await db.execute(select(User).where(User.id == user_uuid))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        logger.info(f"Token refreshed for user: {user.id}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token",
        )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return current_user
