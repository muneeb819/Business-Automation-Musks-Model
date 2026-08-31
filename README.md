# Business Automation — Musk's Model

A multi-tenant SaaS platform that operates an AI-powered Business Development department.

> **Repo:** github.com/muneeb819/Business-Automation-Musks-Model
>
> **Deployment:** Frontend on **Vercel** (`vercel.json` → `rootDirectory: frontend`);
> FastAPI backend on a Python-friendly host (Railway/Render/Fly) connected to a hosted
> **PostgreSQL**. See `docs/DEPLOYMENT.md` for step-by-step.

## Key invariant

The **Outreach Agent is hard-locked the moment a prospect replies**: it sets the lead to
`HUMAN_HANDOFF`, raises `PermissionError` on any further automated send, and notifies a
human — enforced in code, not just by prompt.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                           │
│                    Dashboard & UI                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│                    API & Business Logic                         │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   PostgreSQL    │ │     Redis       │ │    Temporal     │
│  (Source of     │ │  (Cache/State)  │ │  (Workflows)    │
│    Truth)       │ │                 │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Tech Stack

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS
- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic
- **Database:** PostgreSQL
- **Cache:** Redis
- **Workflows:** Temporal
- **Deployment:** Docker, Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Quick Start with Docker

```bash
# Clone the repository
cd ai-bd-platform

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env  # Configure your environment variables
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Leads
- `GET /api/v1/leads/` - List leads
- `POST /api/v1/leads/` - Create lead
- `GET /api/v1/leads/{id}` - Get lead
- `PATCH /api/v1/leads/{id}` - Update lead
- `POST /api/v1/leads/{id}/handoff` - Create human handoff

### Companies
- `GET /api/v1/companies/` - List companies
- `POST /api/v1/companies/` - Create company
- `GET /api/v1/companies/{id}` - Get company
- `PATCH /api/v1/companies/{id}` - Update company

### Approvals
- `GET /api/v1/approvals/` - List approvals
- `POST /api/v1/approvals/` - Create approval
- `GET /api/v1/approvals/{id}` - Get approval
- `POST /api/v1/approvals/{id}/action` - Approve/Reject

### Agents
- `GET /api/v1/agents/` - List agents
- `POST /api/v1/agents/` - Create agent
- `GET /api/v1/agents/{id}` - Get agent
- `PATCH /api/v1/agents/{id}/status` - Update agent status
- `GET /api/v1/agents/{id}/health` - Get agent health score

### Dashboard
- `GET /api/v1/dashboard/overview` - Dashboard overview
- `GET /api/v1/dashboard/pipeline` - Pipeline summary
- `GET /api/v1/dashboard/recent-activity` - Recent activity

## Features

- Multi-tenant architecture with organization isolation
- Role-based access control (RBAC)
- Lead intelligence pipeline
- AI agent management
- Approval workflow system
- Real-time dashboard
- Supervisor command center
- Business memory engine

## Development Status

- [x] Project structure
- [x] Backend API foundation
- [x] Database models
- [x] Authentication system
- [x] Lead management API
- [x] Company management API
- [x] Approval system API
- [x] Agent management API
- [x] Dashboard API
- [x] Frontend layout
- [ ] Lead intelligence pipeline
- [ ] Outreach agent
- [ ] Marketing agents
- [ ] Supervisor agent
- [ ] Optimization agent
- [ ] Temporal workflows
- [ ] Redis integration
- [ ] Testing suite
- [ ] Documentation

## License

Proprietary - All rights reserved
