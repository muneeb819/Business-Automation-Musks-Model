# Deployment & Operations

## Deployment Targets

The application is containerized with Docker and designed to deploy to any cloud provider:

- **Railway / Render / Fly.io** — simplest, good for rapid deployment
- **AWS (ECS/EC2 + RDS + ElastiCache)** — for production scale
- **GCP (Cloud Run + Cloud SQL + Memorystore)**
- **DigitalOcean App Platform + Managed DB**

## Prerequisites

1. PostgreSQL 16+ (managed or self-hosted)
2. Redis 7+
3. Docker & Docker Compose

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | SQLAlchemy async PostgreSQL URL |
| `REDIS_URL` | Yes | Redis connection URL |
| `JWT_SECRET_KEY` | Yes | Long random string for token signing |
| `OPENAI_API_KEY` | No | AI provider key (mock without it) |
| `TEMPORAL_HOST` | No | Temporal server address |

## Local Development

### Option A: Docker Compose (recommended)
```bash
docker-compose up --build
# Frontend: http://localhost:3000
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
```

### Option B: Manual
```bash
# 1. Start PostgreSQL + Redis (docker or local)
# 2. Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed.py  # creates admin user + default agents
uvicorn app.main:app --reload

# 3. Frontend
cd frontend
npm install
npm run dev
```

## Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "description"  # create migration
alembic upgrade head                              # apply
```

## Seeding

```bash
cd backend
export SEED_ADMIN_EMAIL=admin@example.com
export SEED_ADMIN_PASSWORD=YourS3cureP@ss
python seed.py
```

This creates:
- An admin user
- A default organization
- All 11 default AI agents

## Backup & Recovery

- Use managed PostgreSQL daily backups, or `pg_dump` cron job
- Store backups off-site/object storage
- Test restoration quarterly

## Rollback

- **Database:** Alembic `alembic downgrade -1`
- **App:** Revert to previous Docker image tag
- **Feature flags** via approvals never auto-applied, so rollback is trivial

## Monitoring

- Backend `/health` endpoint for load balancer health checks
- Prometheus metrics can be added to FastAPI
- Logs to stdout for cloud log aggregation
