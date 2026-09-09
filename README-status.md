# Deployment Status

Updated: 2026-09-08

## Live URLs
- App: https://business-automation-musks-model.vercel.app (login at `/login`)
- API: https://vercel-pied-psi-35.vercel.app (`/health`, `/api/v1/...`)

## Login (demo/admin)
- Email: `admin@example.com`
- Password: `AdminPassword123!`

## What's Running
- Everything fixed & verified: dashboard, leads, agents (+ detail/health/runs), approvals, pipeline, marketing, outreach. No client-side errors on any page (verified with headless Chrome).
- Database: the API now uses an isolated `ai_bd` schema inside the existing Neon cluster (the API's `DATABASE_URL` had drifted to the legacy `neondb` production DB, which broke login/register; legacy data in `neondb` is untouched).
- Deploys auto-run on `git push` to `main` (latest commit: `c4266fd`).

## Vercel Access
- CLI/API auth restored — `vercel whoami` → `muneeb819` (token saved to the CLI's `auth.json`).
- Deployments still auto-run on `git push` to `main` (latest commit: `c4266fd`).