from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import (
    auth,
    leads,
    companies,
    approvals,
    agents,
    dashboard,
    supervisor,
    campaigns,
    marketing,
    marketplace,
    outreach,
    optimization,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix = settings.API_V1_PREFIX

app.include_router(auth.router, prefix=f"{prefix}/auth", tags=["Authentication"])
app.include_router(leads.router, prefix=f"{prefix}/leads", tags=["Leads"])
app.include_router(companies.router, prefix=f"{prefix}/companies", tags=["Companies"])
app.include_router(campaigns.router, prefix=f"{prefix}/campaigns", tags=["Campaigns"])
app.include_router(approvals.router, prefix=f"{prefix}/approvals", tags=["Approvals"])
app.include_router(agents.router, prefix=f"{prefix}/agents", tags=["Agents"])
app.include_router(supervisor.router, prefix=f"{prefix}/supervisor", tags=["Supervisor"])
app.include_router(marketing.router, prefix=f"{prefix}/marketing", tags=["Marketing"])
app.include_router(marketplace.router, prefix=f"{prefix}/marketplace", tags=["Marketplace"])
app.include_router(outreach.router, prefix=f"{prefix}/outreach", tags=["Outreach"])
app.include_router(dashboard.router, prefix=f"{prefix}/dashboard", tags=["Dashboard"])
app.include_router(optimization.router, prefix=f"{prefix}/optimization", tags=["Optimization"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}


@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }
