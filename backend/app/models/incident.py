import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


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
