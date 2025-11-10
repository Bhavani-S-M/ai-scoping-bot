# backend/app/schemas/project_schemas.py
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime


class ProjectBase(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    complexity: Optional[str] = None
    tech_stack: Optional[str] = None
    use_cases: Optional[str] = None
    compliance: Optional[str] = None
    duration: Optional[str] = None


class ProjectCreate(ProjectBase):
    company_id: Optional[uuid.UUID] = None


class Project(ProjectBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    company_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True