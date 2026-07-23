from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth_routes, incidents

Base.metadata.create_all(bind=engine)  # creates tables if they don't exist

app = FastAPI(title="Smart City Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(incidents.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "Smart City Dashboard API"}
