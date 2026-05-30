# ROADMAP

---

# Current Milestone

Frontend reconstruction and workflow continuity stabilization.

Goal:
- deploy founder-facing frontend
- stabilize workflow UX
- complete backend handoff
- preserve architectural direction

---

# Phase 1 — Rebuild Foundation

## Status: COMPLETE

Completed:
- FastAPI foundation
- modular workflows
- typed APIs
- migrations
- workflow persistence
- revision continuity
- command-center frontend
- assistant rail
- strategy/planning/review flows
- publishing queue foundations

---

# Phase 2 — Operational Hardening

## Status: NEXT PRIORITY

Focus:
- auth/RBAC
- provider abstraction layer
- deployment hardening
- PostgreSQL verification
- workflow reliability
- upload persistence hardening

---

# Phase 3 — Real Integrations

## Future Work

### AI Providers

# ROADMAP — implemented vs in-progress (evidence-based)

This roadmap reflects the current repository contents and does not list aspirational items that have not been started.

## Completed

- Frontend: command-center shell, workspace pages (strategy, planning, review, publishing), assistant rail, sidebar/topbar components, modals and UI primitives (see `frontend/src/components` and `frontend/src/features`).
- Backend: FastAPI app structure, routers for auth/publishing/chat/dashboard, feature routers (`feature_endpoints.py`), platform adapter interfaces, basic approval engine (`approvals/__init__.py`).

## In progress / Partially complete

- Publishing pipeline consolidation — multiple publish paths exist (work in progress):
	- DB-backed `PublishingJob` flows via `routers/publishing.py` (exists)
	- In-memory `PublishingQueue` worker in `workers/queue.py` (exists, not durable)
	- Inline publish path via `routers/chat.py` agent mode (exists, should be gated)
- Provider adapter implementations — adapters exist and support sandbox mode; full live OAuth token lifecycle and publishing verification require provider keys and additional verification.
- Real features integration (`real_features_endpoints.py`): image generation (DALL·E), email service, real trends and metrics collectors exist but depend on external keys.

## Future work (recommended, not yet implemented)

- Consolidate to a single durable publish queue (Redis/Celery or DB-backed worker) and deprecate the in-memory-only queue.
- Commit Alembic migration scripts for current models and add migration CI checks.
- Harden auth and RBAC enforcement around publish/approval transitions.
- Add integration tests that assert publish idempotency and audit logging.
- Complete provider live integration tests (Facebook/Instagram/X/LinkedIn) using the adapter interfaces.

## Notes

- The codebase intentionally uses `SandboxMode` and mock stores during the rebuild; ensure environment variables are validated before enabling any live provider behavior.

---

This roadmap is minimal by design — it only records what is present and what should be prioritized next to reach production readiness.