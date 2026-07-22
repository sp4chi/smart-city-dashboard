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
  **Fix:** *(in progress)* — re-initializing git at the project root; deciding whether to preserve or discard `frontend/`'s standalone history.

### Next
-

---

## Day 2 —

### Goal


### Done
-

### Decisions
-

### Problems & Fixes
-

### Next
-

---

<!-- Duplicate the Day N template above for each new session. -->
