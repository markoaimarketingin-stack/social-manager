# Social Manager

Architectural rebuild of the legacy Social Community Manager platform.

This repository reconstructs the deployed product experience while replacing the unstable legacy architecture with a workflow-oriented, maintainable system.

The rebuild intentionally preserves:
- command-center UX
- operational workflow feel
- premium dark visual identity
- founder-recognizable interaction patterns

while removing:
- fake multi-agent orchestration
- giant mutable frontend state
- hidden synchronization
- tightly coupled frontend/backend logic
- unstable workflow ownership

---

# Product Direction

Social Manager is evolving into:

> An AI-assisted Social Operations OS

The system is workflow-first, not chat-first.

Core philosophy:
- human-in-the-loop operations
- workflow continuity
- revision traceability
- operational clarity
- deterministic state transitions

This rebuild is NOT attempting to recreate:
- fake autonomous AI agents
- distributed orchestration theater
- websocket-heavy synchronization systems

---

# Current Status

The project is currently in:
- frontend reconstruction
- deployment stabilization
- workflow continuity implementation
- backend hardening preparation

The frontend is founder-demo ready.

The backend is architecturally stable but not production-hardened.

Read:
- `PROJECT_STATUS.md`
- `ARCHITECTURE_RULES.md`
- `HANDOFF.md`

before making major architectural changes.

---

# Current Capabilities

## Frontend

Implemented:
- command-center shell
- sidebar reconstruction
- assistant rail reconstruction
- workflow dashboard
- strategy workspace
- planning workspace
- review queue
- publishing queue
- workflow continuity UI
- activity/event surfaces
- operational command-center flows

## Backend

Implemented:
- FastAPI modular monolith
- SQLAlchemy models
- Alembic migrations
- typed API contracts
- workspace-scoped routing
- workflow runs
- activity events
- revision/version lineage
- review progression
- publish-ready queue
- deterministic workflow execution

---

# Real vs Mocked

## Real

- workflow persistence
- revision continuity
- queue persistence
- activity tracking
- workflow lineage
- workspace scoping
- typed APIs
- frontend/backend integration
- uploads infrastructure foundations

## Mocked / Placeholder

- LLM generation
- social publishing providers
- analytics ingestion
- realtime collaboration
- advanced notifications
- OAuth provider auth
- external social APIs

The mocked systems are intentionally deterministic during reconstruction.

---

# Stack

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query
- React Router

## Backend

- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic Settings

## Database

- PostgreSQL-ready
- SQLite-compatible for local verification

---

# Architecture Philosophy

The rebuild follows a strict workflow-oriented architecture.

## Frontend

The frontend is:
- workflow-first
- visually restrained
- operationally sparse
- backend-driven

The frontend should NEVER become:
- dashboard clutter
- giant mutable state
- fake orchestration UI
- websocket-dependent

## Backend

The backend is:
- modular
- deterministic
- typed
- workspace-scoped

The backend intentionally avoids:
- fake agent orchestration
- distributed systems complexity
- hidden workflow synchronization

---

# Workflow Model

The current workflow direction is:

Brand Profile
→ Audience Segments
→ Strategy Generation
→ Content Planning
→ Draft Generation
→ Review Queue
→ Publish Ready
→ Publishing Queue

Workflow lineage and revision continuity are preserved throughout the pipeline.

---

# Local Development

## Environment Setup

Create `.env` from `.env.example`

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

---

# Deployment Status

## Frontend

Frontend is deploy-ready in mock/demo mode.

## Backend

Backend is locally runnable and migration-capable.

Not yet production hardened.

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

## Workflow Runs
- `GET /api/v1/workspaces/{workspace_id}/workflow-runs`
- `POST /api/v1/workspaces/{workspace_id}/strategy-runs`

## Activity
- `GET /api/v1/workspaces/{workspace_id}/activity`
- `GET /api/v1/workspaces/{workspace_id}/activity/summary`

## Publishing Queue
- `GET /api/v1/workspaces/{workspace_id}/drafts/publishing-queue`
- `POST /api/v1/drafts/{draft_id}/publish-ready`
- `POST /api/v1/drafts/{draft_id}/publish`

---

# Important Notes

- The deployed legacy frontend is considered the visual source of truth.
- Preserve visual restraint and cinematic composition.
- Avoid dashboard clutter and operational overload.
- Read `ARCHITECTURE_RULES.md` before major refactors.