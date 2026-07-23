from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas
from .. import models
from ..services import auth_service
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter_by(email=user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        email=user.email,
        hashed_password=auth_service.hash_password(user.password),
        role=user.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token)
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=email).first()
    if not user or not auth_service.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth_service.create_access_token(
        {"sub": str(user.id), "role": user.role.value}
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user
