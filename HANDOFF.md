# HANDOFF

This document exists to help future engineers continue the rebuild safely.

---

# Current Project State

# HANDOFF — quick start for the next engineer

This file is a concise, evidence-based orientation to the current codebase. It is written so a new engineer can understand what exists, where to start, and the known limitations within ~15 minutes.

## One-line summary

Social Manager today is a workflow-first FastAPI monolith with a command-center React frontend (demo-mode). The backend implements posts, publishing jobs, platform adapters (sandboxed), an assistant endpoint, and multiple intelligence feature routers. Several production concerns are intentionally incomplete (durable queue, migrations, auth hardening).

## What works now (implementation evidence)

- Frontend UI: workspace shell, sidebar, assistant panel, workspace pages (strategy, planning, review, publishing) — see `frontend/src/features/*` and `frontend/src/components/layout/*`.
- Backend routers: auth, users, publishing, chat, dashboard, v1_compat, feature routers (`feature_endpoints.py`, `real_features_endpoints.py`) — see `backend/social_manager/routers/`.
- Publishing primitives: `PublishingJob` model usage in routers and an in-memory `PublishingQueue` worker in `backend/social_manager/workers/queue.py`.
- Platform adapters and sandbox: `backend/social_manager/platforms/{base,facebook,instagram,...}` and `SandboxMode` in `platforms/base.py`.
- Approval & policy: `backend/social_manager/approvals/__init__.py` provides `PolicyEngine` and `ApprovalWorkflow` objects.

## What is intentionally mocked or guarded by config

- LLMs: assistant code checks for keys (`GROQ_API_KEY`) and falls back to canned responses if unavailable.
- Provider publishing: adapters use `sandbox=True` by default when credentials are missing and call `SandboxMode.mock_publish` in sandbox mode.
- Real features: many `real_features` services have `initialize()`/`close()` and will fallback to mocks if external keys are not present.

## Key entrypoints and files

- Backend main: `backend/main.py` — app startup, worker initialization
- Routers: `backend/social_manager/routers/*.py` — where HTTP endpoints live
- Feature routers: `backend/social_manager/feature_endpoints.py` and `backend/social_manager/real_features_endpoints.py`
- Platform adapters: `backend/social_manager/platforms/`
- Workers & queue: `backend/social_manager/workers/queue.py` and `backend/social_manager/workers/__init__.py`
- DB models and session: `backend/social_manager/db.py`
- Frontend mock store: `frontend/src/lib/api/mock.ts`

## Important runtime behaviors and gotchas

1. **Multiple publish paths:** publishing can be executed via (A) DB job + background tasks (`routers/publishing.py`), (B) in-memory `PublishingQueue` workers (started by `workers.init_workers()`), and (C) direct synchronous publish from `routers/chat.py` when `agent` mode is used. This duplication is the primary operational complexity.
2. **Global platform_hub singleton:** `platforms/hub.py` exposes a `platform_hub` global and also provides `get_user_platform_hub()` which re-registers per-user adapters. Be careful with global mutation.
3. **Migrations missing:** Alembic exists but no version files are committed. The codebase uses `Base.metadata.create_all()` in some flows — do not assume a migration pipeline is present.
4. **Sandbox defaults:** Many adapters default to sandbox if credentials are absent — watch for unintended 'live' behavior if environment variables are populated.

## Quick tasks for a new engineer who wants to explore

1. Start the backend locally and hit `GET /api/publishing/queue` to see current DB-backed posts and jobs.
2. Inspect `frontend/src/lib/api/mock.ts` to understand how the frontend is wired for demo mode.
3. Review `backend/social_manager/routers/chat.py` to see how assistant `agent` mode currently performs immediate publishes.

## Known assumptions and limitations (evidence)

- The frontend assumes the backend is the source of truth and that workflows are explicit; the backend mostly satisfies this, but there are paths (chat agent) that bypass the canonical enqueue-and-audit flow.
- The expectation that publishing goes through a durable queue is not yet enforced by code — the in-memory queue is not durable.

## Who to ask (if available)

- Look at recent commits by `markoaimarketingin-stack` — large UI and router changes were committed on May 29–30, 2026.

## Next recommended immediate safety moves (if you take over)

1. Gate the chat `agent` publish path behind RBAC and explicit approval or change it to only enqueue a job.
2. Add Alembic migration scripts for the current models before making schema changes.
3. Consolidate publishing execution to a single durable mechanism.

---

This handoff is intentionally short. If you want, I can produce a PR that adds a checklist of protective unit/integration tests and CI checks to prevent accidental publishes during development.