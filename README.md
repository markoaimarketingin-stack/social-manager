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
# Social Manager — current snapshot

This README documents the repository state as implemented in the codebase (May 2026). It describes what the project actually is today, what works, what is mocked, and how to run it locally for development.

Do not read this as a plan or roadmap — it describes implemented systems and known gaps found in the repository.

## Product identity

Social Manager is an AI-assisted Social Operations OS focused on human-in-the-loop workflows for planning, drafting, reviewing and (demo) publishing social posts. The UI is a command-center style web app; the backend is a FastAPI monolith with workflow and publishing primitives.

## High-level architecture (as implemented)

- Frontend: React + TypeScript single-page app (Vite-based). The UI is largely implemented and runs in a demo mode backed by local mock stores.
- Backend: FastAPI monolith with SQLAlchemy models. Routers are organized by feature (auth, publishing, intelligence, chat, dashboard, real_features, etc.).
- Publishing: a DB-backed publishing job model exists and there is also an in-process, in-memory `PublishingQueue` worker. The codebase contains more than one publish execution path (background tasks, in-memory workers, and some inline publishes).
- Providers: modular platform adapters live under `backend/social_manager/platforms/` with an explicit `SandboxMode` used throughout. A `PlatformAdapterHub` factory exists and a global `platform_hub` singleton is present in the code.

## What users can do today (evidence-based)

- Sign in / connect flows exist in the frontend (pages and UI present), though OAuth integrations are still mocked or gated by missing credentials.
- Browse workspace dashboard, trends, strategy, planning, review and publishing UI surfaces in the frontend (pages and components present).
- Use the assistant rail for Q&A and content drafting in the frontend; backend exposes a `POST /api/chat/interact` endpoint which supports `ask` and `agent` modes.
- Schedule and manage posts via REST endpoints; the backend supports creating `Post` records and `PublishingJob` entries and exposes queue endpoints.
- Call intelligence and content-generation endpoints in `feature_endpoints.py` and `real_features_endpoints.py` (trend, competitor, segmentation, copy generation, sentiment, image generation endpoints exist in code).

## What is still mocked or intentionally deterministic

- LLM generation: code contains fallbacks and checks for missing API keys; frontend also uses `frontend/src/lib/api/mock.ts` extensively.
- Social provider publishing: adapters support `SandboxMode` and many adapters default to sandbox when credentials are absent.
- Analytics ingestion and some metrics collectors rely on mock fallbacks.
- OAuth publishing and some external platform integrations are intentionally mocked until provider keys are configured.

## Key API groups (implemented routers)

- `/api/auth` — authentication and OAuth helpers (backend/social_manager/routers/auth.py)
- `/api/publishing` — create/schedule posts, query queue (backend/social_manager/routers/publishing.py)
- `/api/chat` — assistant endpoints with `ask` and `agent` modes (backend/social_manager/routers/chat.py)
- `/api/intelligence/*` — feature intelligence endpoints (backend/social_manager/feature_endpoints.py)
- `/api/real/*` — real-feature endpoints (backend/social_manager/real_features_endpoints.py)
- `/api/dashboard`, `/api/users`, `/api/v1_compat` — other modular routers (see `backend/social_manager/routers/`)

## Frontend status (short)

- UI: largely implemented (command-center shell, sidebar, assistant panel, workspace pages, modals).
- Data binding: frontend relies heavily on `mock.ts` for demo mode; many interactions are wired to the mock store rather than live backend calls by default.

## Backend status (short)

- Core models, routers, and services are present (auth, users, posts, publishing, platform adapters, intelligence modules).
- There is an in-memory `PublishingQueue` with worker loops and a `publishing_service` wrapper in `backend/social_manager/workers/queue.py`.
- Alembic is present but `alembic/versions` is empty in the repository snapshot (the code uses `Base.metadata.create_all()` in some paths). Migrations are not committed.

## Deployment status

- Deployment manifest files exist (`Dockerfile`, `render.yaml`, `vercel.json`) but the application is not production hardened.
- Backend contains development defaults and sandbox fallbacks; do not deploy to production without addressing migrations, durable queues, and auth hardening.

## Setup (local dev) — minimal notes (evidence from repo)

Backend (Python):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend (Node):

```bash
cd frontend
npm install
npm run dev
```

Notes: environment variables in `.env.example` show keys expected (`GROQ_API_KEY`, `twitter_api_key`, `linkedin_client_id`, etc.). Many features require real provider keys to run live.

## Current workflow model (implemented)

- Workflow-first intent is implemented: posts and revisions are stored and the backend tracks workflow progression.
- Publishing is implemented as jobs, but the repository contains multiple mechanisms for executing publishing tasks: FastAPI background tasks calling `execute_publishing_job`, an in-memory `PublishingQueue` worker, and some inline publish paths (chat agent publishing). This multiplicity introduces operational ambiguity.

## Important paths and files

- Backend main application: `backend/main.py`
- Core backend package: `backend/social_manager/`
- Platform adapters: `backend/social_manager/platforms/` (Facebook, Instagram, LinkedIn, X, YouTube)
- Publishing queue + workers: `backend/social_manager/workers/queue.py` and `backend/social_manager/workers/__init__.py`
- Chat assistant router: `backend/social_manager/routers/chat.py`
- Feature routers: `backend/social_manager/feature_endpoints.py`, `backend/social_manager/real_features_endpoints.py`
- Frontend mock API: `frontend/src/lib/api/mock.ts`

## What remains future work (code evidence)

- Durability and migrations: Alembic migration files are missing; production DB migration pipeline not present in repo.
- Auth/RBAC hardening: `approvals` module exists, but `auth` and token lifecycle need production hardening.
- Publish pipeline consolidation: pick a single canonical durable queue (Redis/Celery or DB-backed worker) and remove duplicate inline publishes.
- Clean provider integrations: adapters rely on sandbox by default; complete OAuth flows and provider keys are needed to enable live publishing.

---

If you need a short guided tour of important files next, I can produce a one-page file map highlighting where to start for frontend, backend, and publishing consolidation.
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