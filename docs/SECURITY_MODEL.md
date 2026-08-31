# Security Model

## Authentication

- **Registration:** Creates user + default organization + owner membership
- **Login:** Returns access + refresh JWT tokens
- **Access token:** Short-lived (30 min) for API auth
- **Refresh token:** Longer-lived (7 days), exchanged for new access token
- Passwords hashed with bcrypt via Passlib

## Authorization

- **Memberships** link users to organizations with a role and permission list
- **Role-based access** with granular permissions (not hard-coded role checks)
- **Tenant isolation:** Every query derives `organization_id` from the authenticated user's session, never from request bodies or URL params

## AI Security

**Foundation principle: *Data is not authority.***

External content (webpages, emails, messages, documents, lead profiles) may contain malicious instructions. Therefore:

- Agents have explicitly defined tools with permission/risk metadata
- Agents cannot modify system configuration without approval
- Agents cannot reveal secrets
- Agents cannot bypass approvals
- Agents cannot change permissions
- Agents cannot execute arbitrary tools
- Agents cannot access another tenant
- The **Outreach Agent locks** and cannot act on a lead in `HUMAN_HANDOFF` state

## Protection Controls

- **CSRF protection** via CORS + Origin checking
- **Input validation** via Pydantic schemas on all endpoints
- **Rate limiting** via Redis (`services.redis.rate_limit`)
- **Secure headers** via framework defaults
- **Secret management** via environment variables (never committed)
- **Audit logging** for all significant actions
- **Least-privilege access** enforced through permissions

## Regulatory/Data Notes

- Contact verification respects platform terms and privacy laws (design note)
- The lead discovery architecture is built on authorized/API sources, not scraping services that violate terms (design principle documented in spec)
