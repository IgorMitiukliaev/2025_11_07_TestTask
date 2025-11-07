import datetime
from datetime import timezone
from email.policy import default
import uuid
from sqlalchemy import UUID, Column, String, Text, DateTime, func
from core.enums import IncidentStatus, IncidentSource
from db.session import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default=IncidentStatus.OPEN.value)
    source = Column(String(50), nullable=False, default=IncidentSource.OPERATOR.value)
    created_at = Column(DateTime, nullable=False, default=func.now())
