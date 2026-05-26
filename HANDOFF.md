# HANDOFF

This document exists to help future engineers continue the rebuild safely.

---

# Current Project State

The rebuild is currently:
- visually reconstructed
- architecturally stabilized
- workflow-oriented
- frontend deploy-ready
- backend partially production-shaped

The system is NOT yet production complete.

---

# Current Product Direction

The rebuild evolved away from:
- autonomous multi-agent architecture
- orchestration-heavy systems
- fake AI coordination layers

The product direction is now:

> AI-assisted Social Operations OS

The system is workflow-first and human-in-the-loop.

---

# Frontend Status

The frontend currently includes:
- reconstructed command-center shell
- workflow dashboard
- strategy surfaces
- planning surfaces
- review queue
- publishing queue
- assistant rail
- activity/event UX
- operational continuity UI

The deployed legacy product was used as the visual source of truth.

---

# Backend Status

The backend currently provides:
- workspace-scoped APIs
- workflow persistence
- revision continuity
- queue foundations
- activity events
- deterministic workflows
- typed API contracts

---

# Current Backend Expectations

The frontend expects:
- deterministic request/response APIs
- typed workflow payloads
- workspace-scoped data
- queue visibility
- workflow continuity
- activity timelines

The frontend does NOT assume:
- websocket synchronization
- distributed orchestration
- autonomous agent execution

---

# Still Mocked

These systems are still mocked:
- AI generation
- provider publishing
- analytics ingestion
- OAuth integrations
- advanced notifications
- realtime collaboration

Mocking is intentional during rebuild stabilization.

---

# Recommended Backend Priorities

## Immediate

1. auth/RBAC hardening
2. provider abstraction layer
3. publishing integrations
4. analytics ingestion
5. production DB verification
6. deployment hardening

## NOT Recommended Yet

Avoid:
- microservices
- websocket systems
- distributed orchestration
- event-bus complexity
- autonomous agent systems

---

# Important Frontend Assumptions

Frontend assumes:
- workflows remain explicit
- revision lineage remains visible
- backend is source of truth
- API contracts stay typed

Do NOT:
- reintroduce giant mutable workflow state
- create hidden orchestration synchronization
- overload assistant rail with debugging data

---

# Important Architecture Constraint

The rebuild intentionally replaced the legacy architecture.

Do NOT rebuild the legacy system internally.

Preserve:
- modular workflows
- deterministic flows
- workflow continuity
- restrained UX
- operational clarity