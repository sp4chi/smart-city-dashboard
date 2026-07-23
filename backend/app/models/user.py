import uuid
import enum
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..database import Base


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
