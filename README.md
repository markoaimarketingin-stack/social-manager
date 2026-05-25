# Social Manager

Clean rebuild of the Social Community Manager product.

## Current Scope

This implementation only covers Phase 0 and Sprint 1:

- backend foundation
- database + migrations
- workspace-scoped API structure
- workspaces
- members
- brand profiles
- audience segments
- workflow run tracking foundation
- strategy workflow stub
- frontend app shell
- onboarding workspace setup
- brand profile page
- audience segments page

It does not yet include publishing, analytics, supervisor chat, or multi-agent UX.

## Stack

- Backend: FastAPI, SQLAlchemy 2.x, Alembic, Pydantic Settings
- Database: PostgreSQL-ready configuration
- Frontend: React, TypeScript, Vite, React Router, TanStack Query, Tailwind CSS

## Folder Layout

```text
social-manager/
  backend/
    alembic/
    app/
      api/
      core/
      db/
      middleware/
      modules/
      schemas/
      services/
      workflows/
    tests/
  frontend/
    src/
      app/
      components/
      features/
      lib/
      styles/
  scripts/
  .env.example
```

## Environment Setup

Create a root `.env` file from `.env.example`:

```powershell
Copy-Item .env.example .env
```

## Backend Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

`frontend/vite.config.ts` reads environment variables from the repo root, so `VITE_API_BASE_URL` can stay in the shared root `.env`.

## Key Routes

### System

- `GET /health`
- `GET /api/v1/health`
- `GET /api/v1/system/status`

### Workspaces

- `POST /api/v1/workspaces`
- `GET /api/v1/workspaces/{workspace_id}`

### Brand Profile

- `GET /api/v1/workspaces/{workspace_id}/brand-profile`
- `PUT /api/v1/workspaces/{workspace_id}/brand-profile`

### Audience Segments

- `GET /api/v1/workspaces/{workspace_id}/audience-segments`
- `POST /api/v1/workspaces/{workspace_id}/audience-segments`
- `PUT /api/v1/workspaces/{workspace_id}/audience-segments/{segment_id}`
- `DELETE /api/v1/workspaces/{workspace_id}/audience-segments/{segment_id}`

### Workflow Runs

- `GET /api/v1/workspaces/{workspace_id}/workflow-runs`
- `GET /api/v1/workflow-runs/{workflow_run_id}`
- `POST /api/v1/workspaces/{workspace_id}/strategy-runs`

## Migrations

Initial migration:

- `0001_phase0_foundation`

It creates:

- `workspaces`
- `members`
- `brand_profiles`
- `audience_segments`
- `workflow_runs`

## Notes

- The strategy workflow is intentionally a typed stub for Sprint 1.
- Database access is workspace-scoped through route structure and services.
- The frontend only integrates with routes that actually exist.
