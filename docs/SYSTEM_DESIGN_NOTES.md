# System Design Revision Notes

Generic reference material — not tied to any one project. Revisit this before starting any new build.

---

## 1. System Architecture Basics

**Client → Server → Database → back to Client** is the core loop of almost every web app:

```
Client (React)  --HTTP request-->  Backend (FastAPI)  --query-->  Database (PostgreSQL)
Client (React)  <--JSON response--  Backend (FastAPI)  <--rows--  Database (PostgreSQL)
```

- **Client**: renders UI, sends requests, displays responses. Has no direct DB access.
- **Backend**: business logic, validation, auth, talks to the DB. The only thing that should touch the DB directly.
- **Database**: persistent storage.

### Monolith vs Microservices (high level)
| | Monolith | Microservices |
|---|---|---|
| Structure | One codebase, one deployable | Multiple independent services |
| Best for | Solo/small teams, MVPs, tight timelines | Large teams, independently scaling components |
| Trade-off | Simpler to build/deploy, harder to scale parts independently | More flexible, much higher operational complexity |
| Rule of thumb | **Start monolith.** Split later if/when a specific part needs independent scaling. | Don't reach for this on day 1 of an MVP. |

### Authentication flow (typical)
```
1. User submits credentials -> POST /login
2. Backend verifies against DB (hashed password check)
3. Backend issues a token (JWT) or session
4. Client stores token, sends it in headers on future requests
5. Backend validates token on each protected request
```

### AI integration flow (typical)
```
1. Client sends a user query/action -> backend endpoint
2. Backend assembles context (retrieved docs, DB data, conversation history)
3. Backend calls the AI model API (e.g. Gemini, Claude) with a structured prompt
4. Model returns a response (text or structured JSON)
5. Backend validates/parses, then returns to client
```
Key point: **the client never calls the AI API directly** — always route through your backend so you control the API key, prompt, and validation.

---

## 2. Database Design

- **Table**: a collection of rows with the same columns (e.g. `users`, `incidents`).
- **Primary Key (PK)**: uniquely identifies a row in its own table (usually `id`).
- **Foreign Key (FK)**: a column in one table that references a PK in another table — this is how tables relate.

### Relationship types
| Type | Example | How it's modeled |
|---|---|---|
| One-to-One | A user has one profile | FK with a unique constraint |
| One-to-Many | A zone has many assets | FK on the "many" side (`asset.zone_id`) |
| Many-to-Many | Crews can handle many incident types, incident types can have many crews | A join/bridge table with two FKs |

### ER Diagrams
- Represent entities as boxes, relationships as lines between them, with cardinality (1, many) labeled.
- Draw this **before** writing any backend code — it forces you to think through relationships early.
- Tools: Draw.io, Excalidraw, or Mermaid (`erDiagram` syntax) for text-based diagrams that live in version control.

---

## 3. API Design (REST)

### HTTP methods and what they mean
| Method | Purpose | Idempotent? |
|---|---|---|
| GET | Read data | Yes |
| POST | Create new data | No |
| PUT | Update/replace existing data | Yes |
| DELETE | Remove data | Yes |

### Status codes worth knowing
| Code | Meaning |
|---|---|
| 200 | OK — success |
| 201 | Created — POST succeeded, new resource made |
| 204 | No Content — success, nothing to return (common for DELETE) |
| 400 | Bad Request — client sent invalid data |
| 401 | Unauthorized — missing/invalid auth |
| 403 | Forbidden — authenticated but not allowed |
| 404 | Not Found |
| 500 | Server Error — something broke on the backend |

### Request/Response body
- **Request body**: what the client sends (JSON), mainly on POST/PUT.
- **Response body**: what the server sends back — usually JSON, with a consistent shape (e.g. always `{ data, error }` or similar).

### Naming convention
Use nouns, not verbs, and nest resources logically:
```
GET    /users            # list
GET    /users/:id         # single
POST   /users             # create
PUT    /users/:id         # update
DELETE /users/:id         # delete
```

---

## 4. Product Thinking Vocabulary

- **Functional requirements**: what the system *does* (e.g. "users can log an incident").
- **Non-functional requirements**: how the system *behaves* (e.g. "dashboard loads in under 2 seconds", "handles 100 concurrent users").
- **User persona**: a semi-fictional profile representing a user type (goals, pain points, context).
- **User journey**: the step-by-step path a persona takes through the product to accomplish a goal.
- **MVP vs future features**: MVP = the smallest version that proves the core value; everything else goes in a backlog/roadmap, not into the first build.

---

## 5. Project Structure Rationale

A typical FastAPI backend layout:
```
backend/
├── app/
│   ├── routers/     # API route definitions (grouped by resource)
│   ├── models/      # ORM models (DB table definitions)
│   ├── schemas/      # Pydantic request/response validation shapes
│   ├── services/     # Business logic, kept separate from route handlers
│   └── database/     # DB connection/session setup
```
**Why separate `models` from `schemas`?** Models define what's *stored*; schemas define what's *sent/received* over the API. They often look similar but shouldn't be the same object — this separation prevents accidentally leaking internal fields (like password hashes) in API responses.

**Why `services/`?** Keeps route handlers thin (just parsing input/returning output) and business logic testable/reusable independent of the HTTP layer.

---

## 6. Git & GitHub Basics

```bash
git init                     # start a repo
git clone <url>              # copy an existing repo locally
git add .                    # stage changes
git commit -m "message"      # save a snapshot
git push                     # send commits to remote
git pull                     # fetch + merge remote changes
git branch <name>            # create a branch
git checkout <name>          # switch to a branch
```

**Common pitfall** (learned the hard way on this project): running `git init` inside a subfolder (e.g. `frontend/`) instead of the project root creates a **nested repo**, and the outer repo silently ignores everything inside that subfolder. Always confirm `.git` lives at the project root with:
```bash
find . -maxdepth 2 -name ".git" -type d
```

---

## 7. AI Feature Planning Checklist

Before adding an AI feature, answer:
1. **Where does AI actually help?** (chatbot, recommendation, summarization, OCR, report generation, classification, drafting, insights)
2. **Why AI, specifically?** — could a simpler rule/statistical approach do this instead?
3. **What model?** — match model capability to task complexity/cost.
4. **Input** — what data does it need, and where does that data come from?
5. **Output** — what format, and how does the rest of the app consume it?

Avoid adding AI because it's trendy — every AI feature should map to a specific step in the business workflow it improves.
