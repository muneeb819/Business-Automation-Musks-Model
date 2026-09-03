# Vercel Serverless API Deployment

This directory contains a **serverless-compatible** FastAPI backend for Vercel.

## What Works on Vercel
- REST API endpoints (auth, leads, approvals, dashboard)
- Sync PostgreSQL via `psycopg2`
- JWT authentication
- Vercel Cron for scheduled tasks

## What Does NOT Work (Requires Full Backend)
- Autonomous agents (hunting, enrichment, outreach)
- Temporal workflows
- Background workers
- WebSocket connections
- Long-running 30-day outreach lifecycles
- Connection pooling (asyncpg)

## Deploy to Vercel
1. Go to https://vercel.com/new
2. Import this repo
3. **Root Directory:** `vercel`
4. Add env vars:
   - `DATABASE_URL` (Neon connection string)
   - `JWT_SECRET_KEY` (strong random string)
5. Deploy

## Local Development
```bash
cd vercel
pip install -r requirements.txt
export DATABASE_URL="your-neon-url"
export JWT_SECRET_KEY="your-secret"
uvicorn api.main:app --reload
```

## API Endpoints
- `GET /health` - Health check
- `POST /api/v1/auth/register` - Register
- `POST /api/v1/auth/login` - Login (OAuth2)
- `GET /api/v1/auth/me` - Current user
- `GET /api/v1/leads` - List leads
- `POST /api/v1/leads` - Create lead
- `POST /api/v1/leads/{id}/handoff` - Human handoff
- `GET /api/v1/approvals` - List approvals
- `POST /api/v1/approvals` - Create approval
- `POST /api/v1/approvals/{id}/action` - Approve/reject
- `GET /api/v1/dashboard/overview` - Dashboard stats
- `POST /api/v1/supervisor/command` - Supervisor (mock)

## Note
This is a **serverless subset** of the full backend. For autonomous agents, Temporal workflows, and background processing, deploy the full backend (`backend/`) to Railway/Render/Fly.