# Social Manager

Clean rebuild of the legacy Social Community Manager product.

This repository is a deliberate architectural reconstruction of the original product while preserving the founder-recognizable frontend experience and command-center UX.

The legacy repository contained:
- inconsistent structure
- broken workflow coupling
- frontend/backend entanglement
- missing boundaries
- orchestration confusion
- unstable scaling patterns

This rebuild intentionally separates:
- workflows
- persistence
- transport contracts
- frontend state
- operational UI

while aggressively preserving the visual identity and product atmosphere of the deployed system.

---

# Current Product State

The rebuild now includes:

- reconstructed command-center frontend UX
- workspace onboarding
- brand profile workflows
- audience segment workflows
- strategy generation workflows
- content planning workflows
- draft generation workflows
- review queue foundations
- publishing queue foundations
- workflow timelines
- revision/version continuity
- assistant rail UX
- operational dashboard surfaces
- deterministic workflow execution
- typed API contracts
- workflow lineage persistence
- activity event tracking

The frontend is visually reconstructed to closely resemble the deployed legacy product while using a cleaner architecture underneath.

---

# Current Reality

The system is intentionally in a:
- frontend deployment
- product reconstruction
- workflow stabilization

phase.

Some systems are:
- mocked
- deterministic
- frontend-assisted
- placeholder operational flows

This is intentional during the rebuild phase.

The goal currently is:
- believable product UX
- founder-facing parity
- stable workflow architecture
- clean extensibility

NOT:
- production-scale infrastructure
- distributed orchestration
- realtime systems

---

# Architecture Philosophy

This rebuild intentionally avoids recreating the legacy product’s architectural problems.

## DO NOT reintroduce

- giant mutable frontend state
- fake multi-agent orchestration
- websocket/event complexity
- monolithic providers
- hidden cross-panel synchronization
- frontend/backend coupling
- giant supervisor state blobs
- dashboard overload
- fake AI orchestration semantics

## ALWAYS preserve

- typed API boundaries
- modular workflows
- workspace-scoped services
- deterministic workflows
- isolated persistence boundaries
- frontend visual fidelity
- premium cinematic minimalism
- restrained operational UX
- workflow continuity
- modular frontend composition

Read:
- `ARCHITECTURE_RULES.md`
- `PROJECT_STATUS.md`

before making major changes.

---

# Stack

## Backend
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic Settings

## Frontend
- React
- TypeScript
- Vite
- React Router
- TanStack Query
- Tailwind CSS

## Database
- PostgreSQL-ready
- SQLite-compatible for local verification

---

# Folder Layout

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

  README.md
  PROJECT_STATUS.md
  ARCHITECTURE_RULES.md
  .env.example
```

---

# Environment Setup

Create a root `.env` file from `.env.example`:

```powershell
Copy-Item .env.example .env
```

---

# Backend Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

# Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

`frontend/vite.config.ts` reads environment variables from the repo root.

---

# Frontend Direction

The deployed legacy frontend is considered the visual source of truth.

Frontend work should preserve:
- cinematic minimalism
- restrained spacing
- premium dark command-center feel
- strong focal hierarchy
- sparse operational surfaces
- emotionally convincing UX

Avoid:
- generic SaaS dashboard energy
- operational overload
- excessive widgets
- equal-weight panel density
- overexplaining workflows visually

The goal is emotional parity with the deployed product.

---

# Current Backend Capabilities

Implemented:
- workspace-scoped APIs
- workflow runs
- strategy workflows
- planning workflows
- draft workflows
- review lifecycle foundations
- activity timelines
- revision/version continuity
- publishing queue foundations
- workflow lineage persistence

Current workflows are deterministic and typed.

Real provider integrations are intentionally deferred.

---

# Current Frontend Capabilities

Implemented:
- command-center shell
- sidebar/topbar reconstruction
- assistant rail
- strategy workspace
- planning workspace
- review queue
- publishing queue
- operational dashboard surfaces
- workflow continuity UX
- activity surfaces
- mock operational interactions

The frontend prioritizes:
- visual fidelity
- product feel
- deployment readiness
- founder-facing parity

---

# Not Yet Implemented

The following systems are intentionally incomplete or mocked:

- real LLM provider integrations
- OAuth/provider publishing
- production auth/RBAC
- websocket/realtime systems
- distributed orchestration
- analytics ingestion
- real social publishing
- production observability
- CI/CD hardening
- scalable worker infrastructure

---

# Key API Areas

## System

- `GET /health`
- `GET /api/v1/health`
- `GET /api/v1/system/status`

## Workspaces

- `POST /api/v1/workspaces`
- `GET /api/v1/workspaces/{workspace_id}`

## Brand Profiles

- `GET /api/v1/workspaces/{workspace_id}/brand-profile`
- `PUT /api/v1/workspaces/{workspace_id}/brand-profile`

## Audience Segments

- `GET /api/v1/workspaces/{workspace_id}/audience-segments`
- `POST /api/v1/workspaces/{workspace_id}/audience-segments`
- `PUT /api/v1/workspaces/{workspace_id}/audience-segments/{segment_id}`
- `DELETE /api/v1/workspaces/{workspace_id}/audience-segments/{segment_id}`

## Workflow Runs

- `GET /api/v1/workspaces/{workspace_id}/workflow-runs`
- `GET /api/v1/workflow-runs/{workflow_run_id}`

## Strategy Workflows

- `POST /api/v1/workspaces/{workspace_id}/strategy-runs`

## Activity

- `GET /api/v1/workspaces/{workspace_id}/activity`
- `GET /api/v1/workspaces/{workspace_id}/activity/summary`

## Publishing Queue

- `GET /api/v1/workspaces/{workspace_id}/drafts/publishing-queue`
- `POST /api/v1/drafts/{draft_id}/publish-ready`
- `POST /api/v1/drafts/{draft_id}/publish`

---

# Verification

Verified:
- frontend build
- backend migrations
- workflow persistence
- SQLite migration flow
- route registration
- deterministic workflow execution

Not fully production-verified:
- PostgreSQL deployment
- production hosting
- OAuth/provider flows
- realtime infrastructure

---

# Important Notes

- The rebuild intentionally removed fake orchestration complexity.
- Workflows are intentionally deterministic during reconstruction.
- Frontend visual fidelity currently matters more than backend completeness.
- Preserve product restraint and premium feel during future frontend work.
- Read `ARCHITECTURE_RULES.md` before major refactors.