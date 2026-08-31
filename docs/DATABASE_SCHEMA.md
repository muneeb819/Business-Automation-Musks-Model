# Database Schema

The platform uses PostgreSQL as the source of truth. Below is the entity model.

## Organizations & Tenancy

| Table | Purpose |
|-------|---------|
| `organizations` | Tenant entities (businesses) |
| `users` | Platform users |
| `memberships` | Links users to organizations with roles/permissions |
| `roles` | Named role definitions per organization |

## CRM Core

| Table | Purpose |
|-------|---------|
| `companies` | Companies being prospected |
| `contacts` | People at companies (decision makers) |
| `leads` | Prospecting opportunities through the pipeline |
| `campaigns` | Outreach/marketing campaigns |
| `activities` | Log of every action on a lead |
| `outreach_messages` | Messages sent to leads |
| `conversations` | Human-handled conversations |
| `conversation_messages` | Individual messages in a conversation |

## Agent Operations

| Table | Purpose |
|-------|---------|
| `agents` | Agent instances per organization |
| `agent_runs` | Execution records for each agent task |
| `agent_tools` | Tool definitions with permission/risk metadata |

## Approvals

| Table | Purpose |
|-------|---------|
| `approvals` | Approval requests for system modifications |

## Marketing

| Table | Purpose |
|-------|---------|
| `marketing_activities` | Marketing content/ads/engagement |
| `experiments` | A/B tests |
| `experiment_variants` | Variants within experiments |

## Knowledge

| Table | Purpose |
|-------|---------|
| `knowledge_documents` | Approved organizational knowledge |
| `knowledge_chunks` | Retrievable chunks with embeddings |

## Notifications & Observability

| Table | Purpose |
|-------|---------|
| `notifications` | User notifications |
| `audit_logs` | Immutable action records |
| `daily_snapshots` | Daily operational metrics |

## Integrations

| Table | Purpose |
|-------|---------|
| `integrations` | External provider connections |
| `webhooks` | Webhook endpoints |

## Diagnostic Model

The system can answer: *Who changed this? Why? When? Which agent initiated it? Who approved it?*
