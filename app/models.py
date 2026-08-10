import uuid
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class Job(Base):
    __tablename__ = "jobs"

    # UUIDv4 primary key string (36 chars) to eliminate IDOR vulnerabilities
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_type = Column(String(100), nullable=False)
    status = Column(String(50), default="PENDING")
    result = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())