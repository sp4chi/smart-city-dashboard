import uuid
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class Crew(Base):
    __tablename__ = "crews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    capacity = Column(Integer, default=0)

    incidents = relationship("Incident", back_populates="crew")
