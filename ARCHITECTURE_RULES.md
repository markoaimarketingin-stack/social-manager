# ARCHITECTURE RULES — (updated to reflect current implementation)

These rules are the working constraints for development. They are updated to reflect current repository realities and to prevent further architectural drift.

Read these before making major changes. Implementations that contradict these rules must be approved and documented in the codebase.

---

# Core Philosophy (enforced)

- Prioritize workflow clarity, typed contracts, and modularity.
- Keep frontend visual fidelity and restrained UX.
- Preserve deterministic state transitions and auditability for any side-effecting operation.

The repository is explicitly NOT a distributed AI-agent platform; avoid reintroducing agent-orchestration semantics that autonomously mutate system state.

---

# Backend rules (must follow code)

1. Single canonical publish pipeline: all publishing must flow through a single, durable job mechanism. The code currently contains multiple routes (DB `PublishingJob` + FastAPI background tasks, an in-memory `PublishingQueue`, and inline publish calls). New work should consolidate around one durable mechanism (DB-backed or broker-backed).
2. No direct assistant-or-agent side-effects: assistant/chat endpoints may return drafts or enqueue actions, but must not perform unreviewed synchronous publishes. The code presently contains `agent` mode in `routers/chat.py` which performs immediate publishes — this is a rule violation and must be gated or refactored.
3. Provider adapters must support `sandbox` and `authenticate()` and never silently mutate global state. Avoid global singletons for adapter state; prefer per-request or explicit factory-created hubs.
4. All side-effecting operations (publish, send email, start AB-test, generate and attach image) must produce a persistent audit trail and a workflow record (Post/Job/Artifact) before executing the external action.
5. Never allow in-memory-only job queues to be the only source of truth for production workflows.

---

# Frontend rules

1. The frontend is the command-center UI and should not own canonical workflow truth: the backend is the source of truth. Keep mock stores separated and opt-in for demo mode.
2. Avoid giant global state providers; prefer page-scoped or component-scoped state with typed models.
3. Assistant UI should be ambient — never expose low-level operation metadata (worker ids, raw HTTP responses) to non-admin users.

---

# Workflow rules

1. Workflows must be explicit, typed and traceable. Each workflow step that causes an external mutation must be persisted as a job/event.
2. Approval gates and RBAC must be honored before publish transitions (create → submitted → approved → scheduled → published).
3. Avoid hidden side effects: a UI action should map to an API call that returns a deterministic workflow change; do not rely on client-side heuristics to alter server state.

---

# Publishing and provider integration rules

1. Provider integrations must be encapsulated in adapters implementing `prepare_post`, `publish`, `fetch_metrics`, and `fetch_inbox` (see `platforms/base.py`). Use `SandboxMode` when credentials are not present.
2. All publish requests must be validated against policy engine (`approvals.PolicyEngine`) before enqueueing or execution.
3. Adapter factories (e.g., `get_user_platform_hub`) must not mutate a global singleton without explicit coordinator ownership.

---

# Assistant rules

1. Assistant endpoints can produce content, suggestions, or enqueue jobs — they must not directly perform external side-effects unless the request is explicitly privileged and audited.
2. The assistant rail UI should present generated drafts and require explicit user actions to progress to approval or publish.

---

# State management rules

1. The backend holds canonical state for posts, jobs, approvals and activity events; the frontend must treat local mocks as demo-only overlays.
2. Avoid large mutable client-side blobs that cause divergence from server lineage; prefer small typed DTOs for UI rendering and edits.

---

# Observed drift (must be addressed)

The repository currently contains several implementation details that contradict the rules above and must be reconciled:

- `routers/chat.py` implements an `agent` mode that drafts and then immediately publishes posts (violates Assistant and Backend rules about no direct assistant side-effects).
- There are multiple publish execution paths: DB + background tasks, an in-memory `PublishingQueue`, and inline synchronous publishes. This violates the single-canonical-pipeline rule.
- A global `platform_hub` singleton exists and is initialized at startup (`platforms/hub.py`), creating hidden mutable state. Prefer factory-based construction for per-user hubs.

Document any approved exceptions in a PR and add tests to cover the expected behavior and audit logging.