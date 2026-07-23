# Hands-On Day — FastAPI + Auth + RBAC + DB Design

A build-along guide. Work top to bottom — each section depends on the previous one.

## Suggested time blocks

| Time | Focus                                                         |
| ---- | ------------------------------------------------------------- |
| 1.   | Project setup + DB connection                                 |
| 2.   | ORM models (SQLAlchemy) + Pydantic schemas                    |
| 3.   | Dependency injection (DB session, reusable deps)              |
| 4.   | Auth: register/login, password hashing, JWT                   |
| 5.   | RBAC: role field + permission dependency                      |
| 6.   | Normalization & DB design theory (read while code runs/tests) |

---

## 1. Project Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi "uvicorn[standard]" sqlalchemy psycopg2-binary python-dotenv \
            "python-jose[cryptography]" "passlib[bcrypt]" python-multipart
```

Folder structure:

```
backend/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── deps.py
│   └── routers/
│       ├── auth_routes.py
│       └── incidents.py
├── .env
└── requirements.txt
```

`.env`:

```
DATABASE_URL=postgresql://user:password@localhost:5432/smartcity
SECRET_KEY=replace-with-a-real-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

`Generate secret key`:

```bash
openssl rand -base64 32
```

---

## 2. Database Connection

`app/database.py`:

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

**What each piece does:**

- `engine` — the actual connection pool to Postgres
- `SessionLocal` — a factory that creates DB sessions (transactions) per request
- `Base` — the parent class all your ORM models inherit from

---

## 3. ORM Models (SQLAlchemy)

`app/models.py`:

```python
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class Role(str, enum.Enum):
    admin = "admin"
    staff = "staff"
    crew = "crew"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(Role), default=Role.staff, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Zone(Base):
    __tablename__ = "zones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    district = Column(String)
    population = Column(Integer)

    assets = relationship("Asset", back_populates="zone")
    incidents = relationship("Incident", back_populates="zone")


class Crew(Base):
    __tablename__ = "crews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    capacity = Column(Integer, default=0)

    incidents = relationship("Incident", back_populates="crew")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id"), nullable=False)
    type = Column(String, nullable=False)
    condition_score = Column(Integer, default=100)
    status = Column(String, default="active")

    zone = relationship("Zone", back_populates="assets")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id"), nullable=False)
    crew_id = Column(UUID(as_uuid=True), ForeignKey("crews.id"), nullable=True)
    type = Column(String, nullable=False)
    status = Column(String, default="open")
    priority = Column(String, default="medium")
    reported_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    zone = relationship("Zone", back_populates="incidents")
    crew = relationship("Crew", back_populates="incidents")
```

**Key concepts:**

- `ForeignKey("zones.id")` — creates the FK relationship at the DB level
- `relationship(...)` — lets you do `incident.zone.name` in Python without writing a join manually (SQLAlchemy handles it)
- `back_populates` — links both sides of the relationship (`Zone.incidents` and `Incident.zone` stay in sync)

---

## 4. Pydantic Schemas (Validation)

`app/schemas.py`:

```python
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional
from .models import Role

# ---- Auth ----
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Role = Role.staff

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    role: Role
    class Config:
        from_attributes = True   # lets Pydantic read SQLAlchemy objects directly

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ---- Incidents ----
class IncidentCreate(BaseModel):
    zone_id: UUID
    type: str
    priority: str = "medium"

class IncidentOut(BaseModel):
    id: UUID
    zone_id: UUID
    crew_id: Optional[UUID]
    type: str
    status: str
    priority: str
    reported_at: datetime
    class Config:
        from_attributes = True
```

**Why this matters:** `UserCreate` is what the client sends (plain password). `UserOut` is what the client receives back — notice it has **no `hashed_password` field**. This separation is exactly why models and schemas are different classes: it physically prevents you from accidentally leaking the password hash in an API response.

---

## 5. Dependency Injection

`app/deps.py`:

```python
from sqlalchemy.orm import Session
from .database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Used in any route like this:

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from .deps import get_db

@app.get("/incidents")
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).all()
```

**What's happening:** FastAPI calls `get_db()` before your route runs, gets one DB session, passes it in, and closes it after the response is sent — even if your route raises an error (thanks to `try/finally`). You never manually open/close sessions in your route code.

This is the core DI pattern in FastAPI: **any function using `yield` can be a dependency**, and FastAPI handles the setup/teardown lifecycle for you.

---

## 6. Auth: Password Hashing + JWT

`app/auth.py`:

```python
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
```

**Never store plain-text passwords.** `hash_password` runs a one-way bcrypt hash — even you (the developer) can't reverse it to see the original password. `verify_password` re-hashes the login attempt and compares — it never decrypts the stored hash.

### Register + Login routes

`app/routers/auth_routes.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter_by(email=user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        email=user.email,
        hashed_password=auth.hash_password(user.password),
        role=user.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=email).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}
```

### A dependency to get the current logged-in user

`app/deps.py` (add to it):

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from . import models, auth
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    payload = auth.decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(models.User).filter_by(id=payload.get("sub")).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

Now any route can require login with one line:

```python
@app.get("/auth/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user
```

---

## 7. RBAC (Role-Based Access Control)

You already have `role` on the `User` model. Now gate specific routes by role using another dependency:

`app/deps.py` (add to it):

```python
def require_role(*allowed_roles: str):
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role.value not in allowed_roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return role_checker
```

Usage — only admins can delete an incident:

```python
from ..deps import require_role

@router.delete("/incidents/{incident_id}", status_code=204)
def delete_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin")),
):
    incident = db.query(models.Incident).filter_by(id=incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    db.delete(incident)
    db.commit()
```

**Why this pattern works well:** `require_role("admin")` returns a _new_ dependency function each time, so you can reuse it anywhere with different allowed roles: `require_role("admin", "staff")` for routes multiple roles can access.

---

## 8. Wiring it together

`app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import auth_routes, incidents

Base.metadata.create_all(bind=engine)   # creates tables if they don't exist

app = FastAPI(title="Smart City Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(incidents.router)
```

Run it:

```bash
uvicorn app.main:app --reload --port 8000
```

Test at `http://localhost:8000/docs` — try `/auth/register`, then `/auth/login`, copy the token, click **Authorize** in Swagger UI, paste it, and try a protected route.

---

## 9. Normalization & DB Design Theory

Normalization = organizing tables to eliminate redundant data and avoid update anomalies. Three levels matter most in practice:

### 1NF (First Normal Form)

Each column holds a single, atomic value — no comma-separated lists in a cell.

❌ Bad:

```
Incident: id | type | crew_names
1        | leak | "Alice, Bob"
```

✅ Good: crew assignment is its own relationship (FK on `Incident.crew_id`, or a join table if many crews can work one incident).

### 2NF (Second Normal Form)

Builds on 1NF — every non-key column must depend on the **whole** primary key, not just part of it. This mostly matters when you have a composite key.

Example: if `UtilityReading` had a composite key of `(asset_id, ts)`, a column like `zone_name` would violate 2NF because it depends only on `asset_id` (via the asset's zone), not on `ts`. Fix: don't store `zone_name` on the reading at all — look it up via the `asset → zone` relationship instead. This is exactly why your `UtilityReading` table stores `zone_id` as a FK rather than duplicating zone details.

### 3NF (Third Normal Form)

Builds on 2NF — no column should depend on another **non-key** column (no "transitive" dependencies).

❌ Bad:

```
Asset: id | zone_id | zone_district
```

`zone_district` depends on `zone_id`, not on `Asset.id` directly — that's a transitive dependency. It belongs on the `Zone` table, not duplicated onto `Asset`.
✅ Good: `Asset` just has `zone_id`; look up `district` via `Zone` when needed.

**Why this matters practically:** if `zone_district` were duplicated across 500 asset rows and the district name changed, you'd have to update all 500 rows — miss one and your data is inconsistent. Normalization avoids that by storing each fact in exactly one place.

### When to break normalization (denormalize)

Sometimes real systems intentionally denormalize for read performance (e.g. storing a `zone_name` snapshot directly on an old incident, so historical records don't change if a zone gets renamed later). This is a deliberate trade-off, not a mistake — know the rule, then know when breaking it is justified.

### Applying this to your schema

Your `docs/data-model.md` schema is already normalized: `Zone`, `Asset`, `Incident`, `Crew` each store their own facts once, connected via FKs rather than duplicated fields. That's exactly what 3NF looks like in practice.

---

## Checklist for today

- [ ] Backend runs, connects to Postgres
- [ ] `User`, `Zone`, `Crew`, `Asset`, `Incident` tables created via `Base.metadata.create_all`
- [ ] `/auth/register` and `/auth/login` work in `/docs`
- [ ] `/auth/me` returns the current user when authorized
- [ ] A role-gated route (e.g. DELETE incident) returns 403 for a non-admin, 204 for an admin
- [ ] Can explain 1NF/2NF/3NF out loud using your own schema as the example
