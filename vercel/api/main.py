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

class ApprovalListResponse(BaseModel):
    approvals: List[ApprovalResponse]
    total: int
    page: int
    page_size: int

class AgentResponse(BaseModel):
    id: str
    name: str
    agent_type: str
    status: str
    health_score: float
    total_runs: int
    successful_runs: int
    failed_runs: int
    last_run_at: Optional[str] = None
    created_at: Optional[str] = None

class AgentHealthResponse(BaseModel):
    agent_id: str
    agent_name: str
    availability: float
    execution_success: float
    task_completion: float
    latency: float
    error_rate: float
    output_quality: float
    cost_efficiency: float
    policy_compliance: float
    overall_score: float

class AgentRunResponse(BaseModel):
    id: str
    agent_id: str
    status: str
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    error_message: Optional[str] = None
    tokens_used: int
    cost: float
    duration_ms: Optional[int] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class ActivityResponse(BaseModel):
    id: str
    lead_id: str
    agent_name: str
    action_type: str
    channel: Optional[str] = None
    summary: Optional[str] = None
    created_at: Optional[str] = None

class MarketingActivityResponse(BaseModel):
    id: str
    agent_type: str
    platform: Optional[str] = None
    content_type: Optional[str] = None
    title: Optional[str] = None
    views: int
    engagement_rate: float
    clicks: int
    leads_attributed: int
    spend: float
    status: Optional[str] = None
    created_at: Optional[str] = None

class MarketingListResponse(BaseModel):
    activities: List[MarketingActivityResponse]
    total: int
    page: int
    page_size: int

class MarketingPerfResponse(BaseModel):
    total_views: int
    total_clicks: int
    total_leads_attributed: int
    total_spend: float
    click_rate: float
    cost_per_lead: float
    activity_count: int

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
@app.get("/api/v1/approvals", response_model=ApprovalListResponse)
def list_approvals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        with db.cursor() as cur:
            cur.execute("SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1", (user["id"],))
            org = cur.fetchone()
            if not org:
                raise HTTPException(403, "No organization")
            org_id = org[0]
            
            where = ["organization_id = %s"]
            params = [org_id]
            if status:
                where.append("status = %s")
                params.append(status.upper())
            where_sql = " AND ".join(where)
            
            cur.execute(f"SELECT COUNT(*) FROM approvals WHERE {where_sql}", params)
            total = cur.fetchone()[0]
            
            cur.execute(
                f"SELECT id, category, title, description, proposed_fix, affected_system, risk_level, status, created_at, resolved_at "
                f"FROM approvals WHERE {where_sql} ORDER BY created_at DESC LIMIT %s OFFSET %s",
                params + [page_size, (page - 1) * page_size]
            )
            rows = cur.fetchall()
        
        approvals = [
            ApprovalResponse(
                id=str(r[0]), category=r[1].lower(), title=r[2], description=r[3],
                proposed_fix=r[4], affected_system=r[5], risk_level=r[6] if r[6] else "low",
                status=r[7].lower(), created_at=r[8].isoformat() if r[8] else None,
                resolved_at=r[9].isoformat() if r[9] else None
            ) for r in rows
        ]
        return ApprovalListResponse(approvals=approvals, total=total, page=page, page_size=page_size)
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
            
            cur.execute(
                "SELECT status, COUNT(*) FROM leads WHERE organization_id = %s AND is_deleted = false GROUP BY status",
                (org_id,)
            )
            counts = {row[0].lower(): row[1] for row in cur.fetchall()}
            
            cur.execute("SELECT COUNT(*) FROM agents WHERE organization_id = %s AND status = 'ACTIVE'", (org_id,))
            active_agents = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM agents WHERE organization_id = %s AND status = 'FAILED'", (org_id,))
            failed_agents = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM approvals WHERE organization_id = %s AND status = 'PENDING'", (org_id,))
            pending_approvals = cur.fetchone()[0]
            cur.execute(
                "SELECT COUNT(*) FROM notifications WHERE organization_id = %s AND (is_read = false OR is_read IS NULL)",
                (org_id,)
            )
            unread_notifications = cur.fetchone()[0]
        
        n = lambda k: counts.get(k, 0)
        statuses = ["new", "contacted", "engaged", "ready_to_close", "closed_won", "closed_lost", "human_handoff", "disqualified"]
        return {
            "leads": {
                "total": sum(n(s) for s in statuses),
                "contacted": n("contacted"),
                "engaged": n("engaged"),
                "ready_to_close": n("ready_to_close"),
                "won": n("closed_won"),
                "lost": n("closed_lost"),
                "human_handoffs": n("human_handoff"),
            },
            "agents": {"active": active_agents, "failed": failed_agents},
            "approvals": {"pending": pending_approvals},
            "notifications": {"unread": unread_notifications},
        }
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(500, f"Dashboard failed: {str(e)}")

@app.get("/api/v1/dashboard/pipeline")
def dashboard_pipeline(db=Depends(get_db), user=Depends(get_current_user)):
    try:
        with db.cursor() as cur:
            cur.execute("SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1", (user["id"],))
            org = cur.fetchone()
            if not org:
                raise HTTPException(403, "No organization")
            org_id = org[0]
            
            cur.execute(
                "SELECT status, COUNT(*) FROM leads WHERE organization_id = %s AND is_deleted = false GROUP BY status",
                (org_id,)
            )
            counts = {row[0].lower(): row[1] for row in cur.fetchall()}
        
        keys = ["new", "contacted", "engaged", "ready_to_close", "human_handoff", "closed_won", "closed_lost"]
        return {k: counts.get(k, 0) for k in keys}
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise HTTPException(500, f"Pipeline failed: {str(e)}")

@app.get("/api/v1/dashboard/recent-activity", response_model=List[ActivityResponse])
def recent_activity(db=Depends(get_db), user=Depends(get_current_user)):
    try:
        with db.cursor() as cur:
            cur.execute("SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1", (user["id"],))
            org = cur.fetchone()
            if not org:
                raise HTTPException(403, "No organization")
            org_id = org[0]
            
            cur.execute(
                "SELECT a.id, a.lead_id, a.agent_name, a.action_type, a.channel, a.summary, a.created_at "
                "FROM activities a JOIN leads l ON l.id = a.lead_id "
                "WHERE l.organization_id = %s ORDER BY a.created_at DESC LIMIT 20",
                (org_id,)
            )
            rows = cur.fetchall()
        
        return [
            ActivityResponse(
                id=str(r[0]), lead_id=str(r[1]) if r[1] else None,
                agent_name=r[2], action_type=r[3].lower() if r[3] else "action",
                channel=r[4], summary=r[5],
                created_at=r[6].isoformat() if r[6] else None
            ) for r in rows
        ]
    except Exception as e:
        logger.error(f"Recent activity error: {e}")
        raise HTTPException(500, f"Recent activity failed: {str(e)}")

# ─── Agents ───────────────────────────────────────────────────────────────
@app.get("/api/v1/agents", response_model=List[AgentResponse])
def list_agents(db=Depends(get_db), user=Depends(get_current_user)):
    try:
        with db.cursor() as cur:
            cur.execute("SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1", (user["id"],))
            org = cur.fetchone()
            if not org:
                raise HTTPException(403, "No organization")
            org_id = org[0]
            
            cur.execute(
                "SELECT id, name, agent_type, status, health_score, total_runs, successful_runs, failed_runs, last_run_at, created_at "
                "FROM agents WHERE organization_id = %s ORDER BY created_at ASC",
                (org_id,)
            )
            rows = cur.fetchall()
        
        return [
            AgentResponse(
                id=str(r[0]), name=r[1], agent_type=r[2].lower() if r[2] else "unknown",
                status=r[3].lower() if r[3] else "unknown", health_score=r[4] or 0.0,
                total_runs=r[5] or 0, successful_runs=r[6] or 0, failed_runs=r[7] or 0,
                last_run_at=r[8].isoformat() if r[8] else None,
                created_at=r[9].isoformat() if r[9] else None
            ) for r in rows
        ]
    except Exception as e:
        logger.error(f"List agents error: {e}")
        raise HTTPException(500, f"Failed to list agents: {str(e)}")

@app.get("/api/v1/agents/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT id, name, agent_type, status, health_score, total_runs, successful_runs, failed_runs, last_run_at, created_at "
                "FROM agents WHERE id = %s AND organization_id = (SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1)",
                (agent_id, user["id"])
            )
            r = cur.fetchone()
            if not r:
                raise HTTPException(404, "Agent not found")
        return AgentResponse(
            id=str(r[0]), name=r[1], agent_type=r[2].lower() if r[2] else "unknown",
            status=r[3].lower() if r[3] else "unknown", health_score=r[4] or 0.0,
            total_runs=r[5] or 0, successful_runs=r[6] or 0, failed_runs=r[7] or 0,
            last_run_at=r[8].isoformat() if r[8] else None,
            created_at=r[9].isoformat() if r[9] else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get agent error: {e}")
        raise HTTPException(500, f"Failed to get agent: {str(e)}")

@app.get("/api/v1/agents/{agent_id}/health", response_model=AgentHealthResponse)
def agent_health(agent_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT id, name, health_score FROM agents WHERE id = %s AND organization_id = (SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1)",
                (agent_id, user["id"])
            )
            agent = cur.fetchone()
            if not agent:
                raise HTTPException(404, "Agent not found")
            
            cur.execute(
                "SELECT COUNT(*), "
                "COUNT(*) FILTER (WHERE status NOT IN ('FAILED', 'ERROR')), "
                "COUNT(*) FILTER (WHERE status IN ('FAILED', 'ERROR')), "
                "COALESCE(AVG(duration_ms), 0) "
                "FROM agent_runs WHERE agent_id = %s AND organization_id = (SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1)",
                (agent_id, user["id"])
            )
            total, ok, bad, avg_ms = cur.fetchone()
            total = total or 0
            ok = ok or 0
            bad = bad or 0
            success_rate = (ok / total) if total else 100.0
            error_rate = (bad / total) if total else 0.0
        
        return AgentHealthResponse(
            agent_id=str(agent[0]), agent_name=agent[1], availability=success_rate,
            execution_success=success_rate, task_completion=success_rate,
            latency=avg_ms or 0, error_rate=error_rate, output_quality=success_rate,
            cost_efficiency=100.0 - error_rate, policy_compliance=100.0,
            overall_score=agent[2] or success_rate
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent health error: {e}")
        raise HTTPException(500, f"Failed to get agent health: {str(e)}")

@app.get("/api/v1/agents/{agent_id}/runs", response_model=List[AgentRunResponse])
def agent_runs(agent_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT id, agent_id, status, input_data, output_data, error_message, tokens_used, cost, duration_ms, started_at, completed_at "
                "FROM agent_runs WHERE agent_id = %s AND organization_id = (SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1) "
                "ORDER BY started_at DESC LIMIT 50",
                (agent_id, user["id"])
            )
            rows = cur.fetchall()
        
        return [
            AgentRunResponse(
                id=str(r[0]), agent_id=str(r[1]), status=r[2].lower() if r[2] else "unknown",
                input_data=r[3], output_data=r[4], error_message=r[5],
                tokens_used=r[6] or 0, cost=r[7] or 0.0, duration_ms=r[8],
                started_at=r[9].isoformat() if r[9] else None,
                completed_at=r[10].isoformat() if r[10] else None
            ) for r in rows
        ]
    except Exception as e:
        logger.error(f"Agent runs error: {e}")
        raise HTTPException(500, f"Failed to get agent runs: {str(e)}")

# ─── Marketing ───────────────────────────────────────────────────────────
@app.get("/api/v1/marketing", response_model=MarketingListResponse)
def list_marketing(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        with db.cursor() as cur:
            cur.execute("SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1", (user["id"],))
            org = cur.fetchone()
            if not org:
                raise HTTPException(403, "No organization")
            org_id = org[0]
            
            cur.execute("SELECT COUNT(*) FROM marketing_activities WHERE organization_id = %s", (org_id,))
            total = cur.fetchone()[0]
            
            cur.execute(
                "SELECT id, agent_type, platform, content_type, title, views, engagement_rate, clicks, "
                "leads_attributed, spend, status, created_at "
                "FROM marketing_activities WHERE organization_id = %s ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (org_id, page_size, (page - 1) * page_size)
            )
            rows = cur.fetchall()
        
        activities = [
            MarketingActivityResponse(
                id=str(r[0]), agent_type=r[1].lower() if r[1] else "unknown",
                platform=r[2], content_type=r[3], title=r[4],
                views=r[5] or 0, engagement_rate=r[6] or 0.0, clicks=r[7] or 0,
                leads_attributed=r[8] or 0, spend=r[9] or 0.0, status=r[10],
                created_at=r[11].isoformat() if r[11] else None
            ) for r in rows
        ]
        return MarketingListResponse(activities=activities, total=total, page=page, page_size=page_size)
    except Exception as e:
        logger.error(f"List marketing error: {e}")
        raise HTTPException(500, f"Failed to list marketing: {str(e)}")

@app.get("/api/v1/marketing/performance", response_model=MarketingPerfResponse)
def marketing_performance(db=Depends(get_db), user=Depends(get_current_user)):
    try:
        with db.cursor() as cur:
            cur.execute("SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1", (user["id"],))
            org = cur.fetchone()
            if not org:
                raise HTTPException(403, "No organization")
            org_id = org[0]
            
            cur.execute(
                "SELECT COALESCE(SUM(views), 0), COALESCE(SUM(clicks), 0), COALESCE(SUM(leads_attributed), 0), "
                "COALESCE(SUM(spend), 0), COUNT(*) "
                "FROM marketing_activities WHERE organization_id = %s",
                (org_id,)
            )
            views, clicks, leads, spend, count = cur.fetchone()
        
        click_rate = (clicks / views * 100) if views else 0.0
        cost_per_lead = (spend / leads) if leads else 0.0
        return MarketingPerfResponse(
            total_views=views or 0, total_clicks=clicks or 0,
            total_leads_attributed=leads or 0, total_spend=spend or 0.0,
            click_rate=round(click_rate, 2), cost_per_lead=round(cost_per_lead, 2),
            activity_count=count or 0
        )
    except Exception as e:
        logger.error(f"Marketing performance error: {e}")
        raise HTTPException(500, f"Failed to get marketing performance: {str(e)}")

# ─── Outreach ─────────────────────────────────────────────────────────────
@app.post("/api/v1/outreach/{action}")
def outreach_action(action: str, body: dict, db=Depends(get_db), user=Depends(get_current_user)):
    try:
        lead_id = body.get("lead_id")
        if not lead_id:
            raise HTTPException(400, "Missing lead_id")
        
        with db.cursor() as cur:
            cur.execute("SELECT organization_id FROM memberships WHERE user_id = %s LIMIT 1", (user["id"],))
            org = cur.fetchone()
            if not org:
                raise HTTPException(403, "No organization")
            
            if action == "check_reply":
                has_reply = body.get("has_reply", False)
                if has_reply:
                    cur.execute(
                        "UPDATE leads SET status = 'HUMAN_HANDOFF', handoff_date = %s, assigned_user_id = %s, updated_at = %s "
                        "WHERE id = %s AND organization_id = %s RETURNING id",
                        (datetime.utcnow(), user["id"], datetime.utcnow(), lead_id, org[0])
                    )
                    if not cur.fetchone():
                        raise HTTPException(404, "Lead not found")
                    db.commit()
                    return {"message": "Reply detected. Human handoff created and automated outreach LOCKED.", "status": "handoff"}
                db.commit()
                return {"message": "Reply check complete. No reply detected - automation continues.", "status": "ok"}
            raise HTTPException(400, f"Invalid action: {action}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Outreach action error: {e}")
        raise HTTPException(500, f"Outreach action failed: {str(e)}")

# ─── Supervisor (Mock) ───────────────────────────────────────────────────
@app.post("/api/v1/supervisor/command")
def supervisor_command(cmd: SupervisorCommand, user=Depends(get_current_user)):
    return {
        "response": f"[Serverless Supervisor] Received: '{cmd.command}'. "
                    "Full agent orchestration requires deployed backend with workers."
    }

# ─── Vercel Entry ───────────────────────────────────────────────────────
# This file is the entry point: vercel/api/main.py