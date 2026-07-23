from pydantic import BaseModel, EmailStr
from uuid import UUID
from ..models import Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Role = Role.staff


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    role: Role

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
