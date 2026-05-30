# PROJECT STATUS

---

# Current Phase

# PROJECT STATUS — current snapshot

This document summarizes the repository state based on code present in the workspace (May 30, 2026). All statements are evidence-based and describe what is implemented now.

## High-level completion estimates

- Overall project completion (visual/workflow parity): **~60%**
- Frontend completion: **~80%** (UI pages and components are largely implemented; many flows use the `mock.ts` demo store)
- Backend completion: **~45%** (routers, models, adapters present; durable integrations and migrations incomplete)
- Production readiness: **Low** — critical items (durable queue, migrations, auth hardening) are unfinished.

## Real vs Mocked (short)

- Real/Implemented: workflow persistence, revision lineage, activity timeline, routers for auth/publishing/chat/intelligence, platform adapter interfaces, approval logic, in-memory publishing workers.
- Partial/Mocked: LLM generation fallbacks, provider publishing (SandboxMode), OAuth flows, analytics ingestion, some real integrations in `real_features` guarded by `initialize()`/credentials.

## Recently added/changed systems (observable in git and files)

- `backend/social_manager/platforms/` — platform adapters and `PlatformAdapterHub` (hub + adapters for facebook/instagram/linkedin/x/youtube)
- `backend/social_manager/real_features_endpoints.py` — new "real" feature routers (real trends, metrics, image generation, email, influencer discovery, A/B testing)
- `backend/social_manager/feature_endpoints.py` — intelligence endpoints (trend, competitor, segmentation, copy generation)
- `backend/social_manager/routers/chat.py` — assistant router with `ask` and `agent` modes (agent mode can draft and publish)
- `backend/social_manager/workers/queue.py` — in-memory `PublishingQueue` and `PublishingService`
- `backend/social_manager/workers/__init__.py` — worker initialization that bridges `platform_hub` and publishing worker

## Known limitations (evidence)

- Alembic migrations: `alembic/versions/` is empty; code uses `Base.metadata.create_all()` in places → no committed migrations.
- Multiple publish execution paths: FastAPI background tasks, in-memory `PublishingQueue`, and some inline publishes (chat agent) — risks duplication and divergence.
- In-memory queue is not durable; jobs can be lost if process restarts.
- `platform_hub` global singleton introduces hidden mutable state.
- Chat `agent` mode performs direct publishes without enforced approval or canonical enqueueing.

## Technical debt

- Missing durable queue integration (Redis/Celery/RQ) or DB-backed worker.
- Missing Alembic migration history and migration CI.
- Duplicate publish logic across routers and workers.
- Policy checks and RBAC present but not consistently enforced across all publish entrypoints.

## Immediate priorities (recommended)

1. Consolidate publish pipeline: choose a canonical durable job system and route all publishes through it.
2. Disable or gate chat `agent` direct-publish path until policy/RBAC/approval checks are enforced.
3. Add Alembic migration scripts for current schema and add migration CI.
4. Replace or back the in-memory queue with a durable broker or DB-backed worker.
5. Harden auth flows and enforce RBAC for publish operations.

## Risks

- Risk of accidental live publishes if provider credentials are present and chat `agent` flows are used.
- Data integrity risks due to missing migrations and volatile in-memory queue.
- Operational complexity from global mutable `platform_hub` and multiple publish paths.

---

This page is intentionally concise. See `HANDOFF.md` for file-level entry points and `ARCHITECTURE_RULES.md` for coding constraints and detected drift.