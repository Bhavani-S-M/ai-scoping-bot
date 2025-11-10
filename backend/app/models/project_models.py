# backend/app/models/project_models.py
# backend/app/models/project_models.py
from sqlalchemy import Column, String, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.config.database import Base


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200))  # Increased from 150
    domain = Column(String(200))  # Increased from 100
    complexity = Column(String(50))
    tech_stack = Column(Text)  # Already Text ✓
    use_cases = Column(Text)  # Already Text ✓
    compliance = Column(Text)  # Already Text ✓
    duration = Column(String(300))  # CRITICAL FIX: Increased from 20 to 300
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # No foreign keys, no relationships
    owner_id = Column(UUID(as_uuid=True))
    company_id = Column(UUID(as_uuid=True))


class ProjectFile(Base):
    __tablename__ = "project_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    project_id = Column(UUID(as_uuid=True))


class ProjectPromptHistory(Base):
    __tablename__ = "project_prompt_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True))
    user_id = Column(UUID(as_uuid=True))
    role = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())