# Deployment Status

Updated: 2026-09-11

## Live URLs
- App: https://business-automation-musks-model.vercel.app (login at `/login`)
- API: https://vercel-pied-psi-35.vercel.app (`/health`, `/api/v1/...`)

## Login (demo/admin)
- Email: `admin@example.com`
- Password: `AdminPassword123!`

## What's Running
- Frontend: `npm run build` passes (26 routes, zero errors). Dev server + `next start` verified.
- Backend: FastAPI suite passes **29/29** tests (SQLite). All REST endpoints smoke-tested end-to-end
  through the Next.js `/api` proxy: auth, dashboard (overview/pipeline/recent-activity), leads
  (+ handoff), companies, agents (+ detail/health/runs), approvals (+ action), campaigns,
  marketing (+ performance), outreach (generate-proposal/send/check-reply), notifications
  (list/read/read-all), organization, supervisor (query/command/digest), optimization, marketplace.
- Database: the API uses an isolated `ai_bd` schema inside the existing Neon cluster
  (the API's `DATABASE_URL` had drifted to the legacy `neondb` production DB, which broke
  login/register; legacy data in `neondb` is untouched).
- Deploys auto-run on `git push` to `main`.

## Vercel Access
- CLI/API auth restored — `vercel whoami` → `muneeb819` (token saved to the CLI's `auth.json`).