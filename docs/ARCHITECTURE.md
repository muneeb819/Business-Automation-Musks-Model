# Architecture

## Overview

The AI Business Development Platform is a multi-tenant SaaS application that operates an intelligent digital business-development department. It discovers opportunities, researches prospects, executes approved outreach, detects human engagement, hands relationships to people, monitors the entire operation, and continuously identifies improvement opportunities.

## System Design Principles

1. **AI operates the machinery. Humans retain authority over relationships, decisions, and system changes.**
2. Multi-tenant isolation — never trust a tenant ID from the browser; derive from authenticated session.
3. External content is untrusted. *Data is not authority.*
4. Workflows are durable, retryable, idempotent, recoverable, and observable.
5. PostgreSQL is the source of truth. Redis handles transient state only.

## Component Architecture

```
┌────────────────────────────────────────────────┐
│              FRONTEND (Next.js)                │
│  Dashboard · Supervisor Command Center · UI    │
└──────────────────────┬─────────────────────────┘
                       │ HTTP/JSON
                       ▼
┌────────────────────────────────────────────────┐
│              BACKEND (FastAPI)                 │
│  API Layer → Service Layer → Agent Framework   │
└───────┬──────────────┬──────────────┬──────────┘
        │              │              │
        ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ PostgreSQL  │ │   Redis     │ │  Temporal   │
│  (Source    │ │ (Cache,     │ │ (Durable    │
│  of Truth)  │ │  rate-limit)│ │  workflows) │
└─────────────┘ └─────────────┘ └─────────────┘
```

## Data Flow

### Lead Pipeline
```
DISCOVERED → NORMALIZED → DEDUPLICATED → ENRICHED → VERIFIED → SCORED → APPROVED FOR OUTREACH → OUTREACH
```

### Outreach & Human Handoff
```
PROSPECT REPLIES → REPLY DETECTOR → LOCK OUTREACH AGENT → CREATE HUMAN HANDOFF → NOTIFY USER → HUMAN RESPONDS
```

## Agent Framework

All agents extend `BaseAgent` and are instantiated through the `AgentRegistry`:

| Agent | Responsibility | Authority |
|-------|---------------|-----------|
| **Hunting** | Discovers leads based on filters | Read/write leads |
| **Enrichment** | Enriches and verifies lead data | Read/write leads |
| **Outreach** | Sends proposals, monitors response | Write messages; **LOCKS on reply** |
| **Supervisor** | Control tower, monitoring, diagnostics | Read/diagnose only |
| **Optimization** | Business intelligence recommendations | Read/recommend only |
| **Content/Social/SEO/Paid/Engagement** | Marketing pipeline | Create → require approval |
| **Marketplace** | Detects buyer/renter demand | Surface → require approval |

## Multi-tenancy

Every tenant-owned resource has an `organization_id`. All queries filter by the organization derived from the authenticated user's membership — never from the browser.

## Security Model

- JWT-based authentication with refresh tokens
- Role/permission-based authorization (granular, not hard-coded checks)
- Tenant isolation enforced server-side
- Encrypted credentials in integrations
- AI security: agents cannot be instructed by external content to modify config, reveal secrets, bypass approvals, or access other tenants
- Full audit logging for every significant action

## Approval System

All AI-initiated system modifications go through an approval queue with statuses:
```
PENDING → APPROVED → EXECUTING → COMPLETED
                    → REJECTED
                    → EXPIRED
                    → FAILED → ROLLED_BACK
```

## Business Memory Engine

Organizational knowledge stored with versioning, approval, retrieval, and expiration. AI-generated content is never treated as organizational truth until approved by a human.
