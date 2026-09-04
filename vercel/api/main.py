"""
Vercel Serverless API - Stripped down version for Vercel Python runtime.
No background workers, no Temporal, no asyncpg - just REST endpoints.
"""
import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Generator

import psycopg
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

# ─── Logging ─────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Config ──────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ─── Database Connection ─────────────────────────────────────────────────
_db_pool = None

def get_conninfo() -> str:
    """Build a psycopg3-compatible connection string for Neon."""
    url = DATABASE_URL
    if not url:
        raise RuntimeError("DATABASE_URL environment variable not set")
    # Convert asyncpg URL to a standard postgres URL
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://")
    # Neon requires SSL - ensure sslmode=require is present
    if "sslmode=" not in url:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}sslmode=require"
    return url

def get_db_pool():
    """Get or create database pool with proper SSL handling for Neon."""
    global _db_pool
    if _db_pool is None:
        try:
            _db_pool = ConnectionPool(
                get_conninfo(),
                min_size=0,
                max_size=3,
                open=False,
                kwargs={"connect_timeout": 10},
            )
            logger.info("Database pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise
    return _db_pool

def get_db() -> Generator:
    """Get database connection from pool (psycopg3)."""
    pool = get_db_pool()
    pool.open(wait=False)
    with pool.connection() as conn:
        try:
            yield conn
        except Exception as e:
            logger.error(f"Database error: {e}")
            try:
                conn.rollback()
            except Exception:
                pass
            raise

# ─── Config Validation ───────────────────────────────────────────────────
if not os.getenv("JWT_SECRET_KEY"):
    logger.warning("JWT_SECRET_KEY not set, using default (INSECURE)")

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ─── Security ────────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(p: str, h: str) -> bool:
    return pwd_context.verify(p, h)

def create_token(data: dict, expires: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    with db.cursor() as cur:
        cur.execute("SELECT id, email, full_name, is_active FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    return {"id": str(row[0]), "email": row[1], "full_name": row[2], "is_active": row[3]}

# ─── Schemas ─────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool

class LeadCreate(BaseModel):
    company_id: Optional[str] = None
    contact_id: Optional[str] = None
    campaign_id: Optional[str] = None
    source: str = "manual_import"
    source_detail: Optional[str] = None
    source_url: Optional[str] = None
    personalization_data: dict = {}
    tags: List[str] = []
    notes: Optional[str] = None

class LeadResponse(BaseModel):
    id: str
    company_id: Optional[str]
    contact_id: Optional[str]
    source: str
    status: str
    fit_score: float
    lead_score: float
    outreach_count: int
    created_at: str
    last_activity_date: Optional[str] = None

class LeadListResponse(BaseModel):
    leads: List[LeadResponse]
    total: int
    page: int
    page_size: int

class ApprovalCreate(BaseModel):
    category: str
    title: str
    description: str
    proposed_fix: str
    affected_system: Optional[str] = None
    risk_level: str = "low"
    expected_impact: Optional[str] = None
    evidence: Optional[str] = None
    rollback_strategy: Optional[str] = None

class ApprovalResponse(BaseModel):
    id: str
    category: str
    title: str
    description: str
    proposed_fix: str
    affected_system: Optional[str]
    risk_level: str
    status: str
    created_at: str
    resolved_at: Optional[str] = None

class ApprovalAction(BaseModel):
    action: str
    notes: Optional[str] = None

class SupervisorCommand(BaseModel):
    command: str

# ─── App ─────────────────────────────────────────────────────────────────
app = FastAPI(title="AI BD Platform API (Serverless)", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# ─── Health ──────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-bd-platform-api-serverless"}

# ─── Auth ────────────────────────────────────────────────────────────────
@app.post("/api/v1/auth/register", response_model=UserResponse)
def register(user: UserCreate, db=Depends(get_db)):
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email = %s", (user.email,))
            if cur.fetchone():
                raise HTTPException(400, "Email already registered")
            
            user_id = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO users (id, email, hashed_password, full_name, is_active, is_superuser, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (user_id, user.email, hash_password(user.password), user.full_name, True, False, datetime.utcnow(), datetime.utcnow())
            )
            db.commit()
        return {"id": user_id, "email": user.email, "full_name": user.full_name, "is_active": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(500, f"Registration failed: {str(e)}")

@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id, email, hashed_password, full_name, is_active FROM users WHERE email = %s", (form.username,))
            row = cur.fetchone()
        if not row or not verify_password(form.password, row[2]):
            raise HTTPException(401, "Invalid credentials")
        if not row[4]:
            raise HTTPException(401, "Inactive user")
        
        token = create_token({"sub": str(row[0]), "email": row[1]})
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(500, f"Login failed: {str(e)}")

@app.get("/api/v1/auth/me", response_model=UserResponse)
def me(user=Depends(get_current_user)):
    return user

# ─── Leads ───────────────────────────────────────────────────────────────
@app.get("/api/v1/leads", response_model=LeadListResponse)
def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        where = ["organization_id = (SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1)", "is_deleted = false"]
        params = [user["id"]]
        
        if status:
            where.append("status = %s")
            params.append(status.upper())
        
        where_sql = " AND ".join(where)
        
        with db.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM leads WHERE {where_sql}", params)
            total = cur.fetchone()[0]
            
            cur.execute(
                f"SELECT id, company_id, contact_id, source, status, fit_score, lead_score, outreach_count, created_at, last_activity_date "
                f"FROM leads WHERE {where_sql} ORDER BY created_at DESC LIMIT %s OFFSET %s",
                params + [page_size, (page - 1) * page_size]
            )
            rows = cur.fetchall()
        
        leads = [
            LeadResponse(
                id=str(r[0]), company_id=str(r[1]) if r[1] else None,
                contact_id=str(r[2]) if r[2] else None, source=r[3].lower(), status=r[4].lower(),
                fit_score=r[5], lead_score=r[6], outreach_count=r[7],
                created_at=r[8].isoformat() if r[8] else None,
                last_activity_date=r[9].isoformat() if r[9] else None
            ) for r in rows
        ]
        return LeadListResponse(leads=leads, total=total, page=page, page_size=page_size)
    except Exception as e:
        logger.error(f"List leads error: {e}")
        raise HTTPException(500, f"Failed to list leads: {str(e)}")

@app.post("/api/v1/leads", response_model=LeadResponse, status_code=201)
def create_lead(lead: LeadCreate, db=Depends(get_db), user=Depends(get_current_user)):
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1", (user["id"],)
            )
            org = cur.fetchone()
            if not org:
                raise HTTPException(403, "No organization")
            org_id = org[0]
            
            lead_id = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO leads (id, organization_id, company_id, contact_id, campaign_id, source, source_detail, source_url, "
                "personalization_data, tags, notes, status, fit_score, lead_score, outreach_count, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (lead_id, org_id, lead.company_id, lead.contact_id, lead.campaign_id,
                 lead.source.upper(), lead.source_detail, lead.source_url, Jsonb(lead.personalization_data),
                 Jsonb(lead.tags), lead.notes, "NEW", 0.0, 0.0, 0, datetime.utcnow(), datetime.utcnow())
            )
            db.commit()
            
            cur.execute(
                "SELECT id, company_id, contact_id, source, status, fit_score, lead_score, outreach_count, created_at, last_activity_date "
                "FROM leads WHERE id = %s", (lead_id,)
            )
            r = cur.fetchone()
        
        return LeadResponse(
            id=str(r[0]), company_id=str(r[1]) if r[1] else None,
            contact_id=str(r[2]) if r[2] else None, source=r[3].lower(), status=r[4].lower(),
            fit_score=r[5], lead_score=r[6], outreach_count=r[7],
            created_at=r[8].isoformat() if r[8] else None,
            last_activity_date=r[9].isoformat() if r[9] else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create lead error: {e}")
        raise HTTPException(500, f"Failed to create lead: {str(e)}")

@app.post("/api/v1/leads/{lead_id}/handoff")
def handoff_lead(lead_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    try:
        with db.cursor() as cur:
            cur.execute(
                "UPDATE leads SET status = 'HUMAN_HANDOFF', handoff_date = %s, assigned_user_id = %s, updated_at = %s "
                "WHERE id = %s AND organization_id = (SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1) "
                "RETURNING id",
                (datetime.utcnow(), user["id"], datetime.utcnow(), lead_id, user["id"])
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(404, "Lead not found")
            db.commit()
        return {"message": "Human handoff created", "lead_id": lead_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Handoff error: {e}")
        raise HTTPException(500, f"Handoff failed: {str(e)}")

# ─── Approvals ───────────────────────────────────────────────────────────
@app.get("/api/v1/approvals", response_model=List[ApprovalResponse])
def list_approvals(db=Depends(get_db), user=Depends(get_current_user)):
    try:
        with db.cursor() as cur:
            cur.execute("SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1", (user["id"],))
            org = cur.fetchone()
            if not org:
                raise HTTPException(403, "No organization")
            org_id = org[0]
            
            cur.execute(
                "SELECT id, category, title, description, proposed_fix, affected_system, risk_level, status, created_at, resolved_at "
                "FROM approvals WHERE organization_id = %s ORDER BY created_at DESC",
                (org_id,)
            )
            rows = cur.fetchall()
        
        return [
            ApprovalResponse(
                id=str(r[0]), category=r[1].lower(), title=r[2], description=r[3],
                proposed_fix=r[4], affected_system=r[5], risk_level=r[6],
                status=r[7].lower(), created_at=r[8].isoformat() if r[8] else None,
                resolved_at=r[9].isoformat() if r[9] else None
            ) for r in rows
        ]
    except Exception as e:
        logger.error(f"List approvals error: {e}")
        raise HTTPException(500, f"Failed to list approvals: {str(e)}")

@app.post("/api/v1/approvals", response_model=ApprovalResponse, status_code=201)
def create_approval(approval: ApprovalCreate, db=Depends(get_db), user=Depends(get_current_user)):
    try:
        with db.cursor() as cur:
            cur.execute("SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1", (user["id"],))
            org = cur.fetchone()
            if not org:
                raise HTTPException(403, "No organization")
            org_id = org[0]
            
            aid = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO approvals (id, organization_id, requester_id, category, title, description, proposed_fix, "
                "affected_system, risk_level, expected_impact, evidence, rollback_strategy, status, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (aid, org_id, user["id"], approval.category.upper(), approval.title, approval.description,
                 approval.proposed_fix, approval.affected_system, approval.risk_level,
                 approval.expected_impact, approval.evidence, approval.rollback_strategy,
                 "PENDING", datetime.utcnow(), datetime.utcnow())
            )
            db.commit()
            
            cur.execute(
                "SELECT id, category, title, description, proposed_fix, affected_system, risk_level, status, created_at, resolved_at "
                "FROM approvals WHERE id = %s", (aid,)
            )
            r = cur.fetchone()
        
        return ApprovalResponse(
            id=str(r[0]), category=r[1].lower(), title=r[2], description=r[3],
            proposed_fix=r[4], affected_system=r[5], risk_level=r[6],
            status=r[7].lower(), created_at=r[8].isoformat() if r[8] else None,
            resolved_at=r[9].isoformat() if r[9] else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create approval error: {e}")
        raise HTTPException(500, f"Failed to create approval: {str(e)}")

@app.post("/api/v1/approvals/{approval_id}/action")
def action_approval(approval_id: str, action: ApprovalAction, db=Depends(get_db), user=Depends(get_current_user)):
    try:
        with db.cursor() as cur:
            cur.execute("SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1", (user["id"],))
            org = cur.fetchone()
            if not org:
                raise HTTPException(403, "No organization")
            
            if action.action not in ("approve", "reject"):
                raise HTTPException(400, "Invalid action")
            
            new_status = "APPROVED" if action.action == "approve" else "REJECTED"
            cur.execute(
                "UPDATE approvals SET status = %s, approver_id = %s, approval_notes = %s, resolved_at = %s, updated_at = %s "
                "WHERE id = %s AND organization_id = %s AND status = 'PENDING' RETURNING id",
                (new_status, user["id"], action.notes, datetime.utcnow(), datetime.utcnow(), approval_id, org[0])
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(404, "Approval not found or not pending")
            db.commit()
        
        return {"message": f"Approval {action.action}d", "approval_id": approval_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Action approval error: {e}")
        raise HTTPException(500, f"Action failed: {str(e)}")

# ─── Dashboard ───────────────────────────────────────────────────────────
@app.get("/api/v1/dashboard/overview")
def dashboard_overview(db=Depends(get_db), user=Depends(get_current_user)):
    try:
        with db.cursor() as cur:
            cur.execute("SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1", (user["id"],))
            org = cur.fetchone()
            if not org:
                raise HTTPException(403, "No organization")
            org_id = org[0]
            
            cur.execute("SELECT COUNT(*) FROM leads WHERE organization_id = %s", (org_id,))
            total = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM leads WHERE organization_id = %s AND status = 'HUMAN_HANDOFF'", (org_id,))
            handoffs = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM leads WHERE organization_id = %s AND status = 'CLOSED_WON'", (org_id,))
            won = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM approvals WHERE organization_id = %s AND status = 'PENDING'", (org_id,))
            pending = cur.fetchone()[0]
        
        return {
            "leads": {"total": total, "human_handoffs": handoffs, "won": won},
            "approvals": {"pending": pending}
        }
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(500, f"Dashboard failed: {str(e)}")

# ─── Supervisor (Mock) ───────────────────────────────────────────────────
@app.post("/api/v1/supervisor/command")
def supervisor_command(cmd: SupervisorCommand, user=Depends(get_current_user)):
    return {
        "response": f"[Serverless Supervisor] Received: '{cmd.command}'. "
                    "Full agent orchestration requires deployed backend with workers."
    }

# ─── Vercel Entry ───────────────────────────────────────────────────────
# This file is the entry point: vercel/api/main.py