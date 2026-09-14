from sqlalchemy import Column, Integer, String, Text
from pydantic import BaseModel, ConfigDict

from app.core.db import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True, nullable=False)
    category_label = Column(String, nullable=False)
    location = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Integer, nullable=False)  # 1 (low) - 5 (high)
    outcome = Column(String, nullable=False)
    days_ago = Column(Integer, nullable=False)


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    category_label: str
    location: str
    description: str
    severity: int
    outcome: str
    days_ago: int


class IncidentCreate(BaseModel):
    category: str
    category_label: str
    location: str
    description: str
    severity: int
    outcome: str
    days_ago: int = 0
