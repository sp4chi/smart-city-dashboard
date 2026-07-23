# Development Log

A running journal of decisions, milestones, problems, and fixes throughout the build. Add a new entry each session/day — this becomes the "story" of the project for demos, retros, or write-ups.

---

## How to use this log

Each entry follows this format:

```
## Day N — YYYY-MM-DD

### Goal
What I set out to do today.

### Done
- Bullet list of what was actually completed.

### Decisions
- Any design/architecture choices made, and why.

### Problems & Fixes
- Problem encountered → root cause → how it was fixed.

### Next
- What's queued up for next session.
```

---

## Day 0 — Planning

### Goal

Define product scope and architecture before writing code.

### Done

- Defined product: AI-native operations platform for city administrators covering utilities, transport, infrastructure, and public services.
- Mapped problem statement tracks (B10–E10) onto a single 4-layer architecture: Data & Integration → Core Operations → AI Intelligence → Command Layer.
- Chose primary users: city administrators/staff (not citizens) as the core workflow owner.
- Drafted core data model: `Zone`, `Asset`, `UtilityReading`, `Incident`, `Crew`, `PolicyDocument`, `Insight`.
- Decided on mock data strategy: 8–12 zones, 15–30 assets/zone, 90 days of hourly time-series readings, hand-scripted anomalies correlated with incidents (for a reliable demo).

### Decisions

- Scoped down to 2–3 utility types (electricity, water, traffic) instead of covering everything — keeps mock data and AI models manageable in a 2-week solo timeline.
- Chose hand-scripted anomaly injection over fully procedural generation, to guarantee the AI advisor has a compelling story during the demo.

### Next

- Set up repo structure (backend/frontend).
- Write seed script for mock data.

---

## Day 1 —

### Goal

### Done

-

### Decisions

-

### Problems & Fixes

- **Problem:** `npm run dev` scripts assumed a Node backend, but backend is FastAPI (Python).
  **Fix:** Rewrote root `package.json` scripts to create a Python venv and run `uvicorn` directly instead of `npm install --prefix backend`.

- **Problem:** Git wasn't tracking changes in `backend/` or root files.
  **Root cause:** `.git` was initialized inside `frontend/` only — no repo existed at the project root, so nothing outside `frontend/` was ever tracked.
  **Fix:** _(in progress)_ — re-initializing git at the project root; deciding whether to preserve or discard `frontend/`'s standalone history.

### Next

- ***

## Day 2 — 2026-07-23

### Goal

Get hands-on with FastAPI: implement dependency injection, authentication, RBAC,
connect the database, build ORM classes with SQLAlchemy, add Pydantic validation.
Also study normalization and DB design theory.

### Done

- Restructured backend into split-file layout: `app/models/`, `app/schemas/`,
  `app/routers/`, `app/services/`, with shared `database.py` and `deps.py` at
  the `app/` root and `main.py` inside `app/`.
- Built SQLAlchemy ORM models: `User` (with `Role` enum), `Zone`, `Crew`, `Asset`, `Incident`.
- Built Pydantic schemas for request/response validation (`UserCreate`, `UserOut`,
  `Token`, `IncidentCreate`, `IncidentOut`), kept separate from ORM models so
  API responses never leak internal fields (e.g. `hashed_password`).
- Implemented dependency injection: `get_db` (DB session per request),
  `get_current_user` (JWT-based auth), `require_role` (RBAC gate).
- Implemented auth service: password hashing (bcrypt via passlib) and JWT
  create/decode (`python-jose`).
- Built `auth_routes.py` (`/auth/register`, `/auth/login`, `/auth/me`) and
  `incidents.py` (list/get/create/delete, with delete gated to `admin` role).
- Connected the backend to a hosted Postgres instance on Neon (pooled connection
  string, SSL required).
- Verified full auth flow end-to-end through Swagger UI (`/docs`): register →
  login → authorize → `/auth/me` → RBAC-gated delete (403 for non-admin, 204 for admin).
- Organized commits into separate feature branches per folder
  (`feature/models`, `feature/schemas`, `feature/services`, `feature/routers`,
  `feature/core-setup`), merged back into `master`.
- Studied normalization (1NF/2NF/3NF) and DB design theory, applied to own schema.

### Decisions

- Kept `models` and `schemas` as separate packages (not combined) — models
  define DB shape, schemas define API shape. Deliberate boundary to prevent
  leaking sensitive fields in responses.
- Used PUT (not PATCH) for updates for now — simpler for MVP; revisit PATCH
  later if partial updates (e.g. "just update status") become common.
- Feature-branch-per-folder git workflow: branched from `master` each time
  (not stacked on each other) so branches stay independent and mergeable in
  any order.

### Problems & Fixes

- **Problem:** `ModuleNotFoundError: No module named 'app.app'`
  **Root cause:** typo in `app/models/user.py` — `from ..app.database import Base`
  instead of `from ..database import Base`.
  **Fix:** corrected the relative import path.

- **Problem:** `sqlalchemy.exc.OperationalError: SSL SYSCALL error: EOF detected`
  when connecting to Neon.
  **Root cause:** Neon's serverless compute suspends after inactivity and can
  drop the first connection attempt on wake; pooled endpoint occasionally
  flaky for long-lived DDL operations like `create_all`.
  **Fix:** added `pool_pre_ping=True` to the SQLAlchemy engine for automatic
  reconnection on stale connections; retried after Neon's compute woke up.

- **Problem:** `ValueError: password cannot be longer than 72 bytes` during
  login, even with a short password.
  **Root cause:** version incompatibility between `passlib` and newer `bcrypt`
  (4.1+) — a known bug, not an actual password-length issue.
  **Fix:** pinned `bcrypt==4.0.1` in `requirements.txt`.

- **Problem:** `requirements.txt` was missing packages needed for auth
  (`python-jose`, `passlib[bcrypt]`, `python-multipart`), and was initially
  located outside `backend/`, not matching the install script's expected path.
  **Fix:** merged and moved `requirements.txt` into `backend/`, added the
  missing packages.

- **Problem:** `__pycache__` was accidentally tracked in git.
  **Fix:** `git rm -r --cached backend/app/__pycache__`, confirmed
  `__pycache__/`, `*.pyc`, `venv/`, `.env` are all in `.gitignore`.

### Next

- Build `zones` and `crews` routers (currently missing — incident creation
  required a manual SQL insert as a workaround since there's no API-driven
  way to create a zone yet).
- Test full incident-creation flow end-to-end via Swagger without manual DB inserts.
- Continue toward AI layer (trend prediction, RAG) per original 2-week timeline.

---

<!-- Duplicate the Day N template above for each new session. -->
