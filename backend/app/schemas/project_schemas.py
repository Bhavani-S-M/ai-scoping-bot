# backend/app/schemas/project_schemas.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
from enum import Enum


class ComplexityLevel(str, Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"


class RefinementIntent(str, Enum):
    MODIFY_TASKS = "modify_tasks"
    ADJUST_TIMELINE = "adjust_timeline"
    APPLY_DISCOUNT = "apply_discount"
    MODIFY_RESOURCES = "modify_resources"
    GENERIC = "generic"
    ERROR = "error"


class ProjectBase(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    complexity: Optional[ComplexityLevel] = None
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


# Enhanced Scope Schemas
class ActivityPhase(BaseModel):
    name: str
    description: str
    effort_days: int
    dependencies: List[str]
    resources_needed: List[str]


class TimelinePhase(BaseModel):
    phase_name: str
    duration_weeks: int
    start_week: int
    end_week: int
    milestones: List[str]


class ResourceAllocation(BaseModel):
    role: str
    count: int
    effort_months: float
    allocation_percentage: int
    monthly_rate: float
    total_cost: float


class CostBreakdown(BaseModel):
    total_cost: float
    contingency_percentage: float
    contingency_amount: float
    discount_applied: Optional[float] = 0
    subtotal: Optional[float] = 0


class DiagramData(BaseModel):
    diagram_type: str
    format: str
    code: str
    description: str


class ScopeMetadata(BaseModel):
    confidence_score: float
    rag_sources_count: int
    generated_at: str
    version: str
    refinement_count: int = 0


class ProjectScope(BaseModel):
    overview: Dict[str, Any]
    activities: List[ActivityPhase]
    timeline: Dict[str, Any]
    resources: List[ResourceAllocation]
    cost_breakdown: CostBreakdown
    diagrams: Dict[str, DiagramData]
    metadata: ScopeMetadata
    assumptions: List[str]
    dependencies: List[Dict[str, Any]]


# Refinement Schemas
class RefinementRequest(BaseModel):
    message: str
    current_scope: Dict[str, Any]
    project_id: uuid.UUID


class RefinementResponse(BaseModel):
    updated_scope: Dict[str, Any]
    response: str
    changes_made: List[str]
    intent: RefinementIntent


class FinalizeRequest(BaseModel):
    scope_data: Dict[str, Any]
    user_feedback: Optional[str] = None
    approval_status: str = "approved"
    export_formats: List[str] = ["pdf", "excel", "json"]


class ExportRequest(BaseModel):
    scope_data: Dict[str, Any]
    format: str
    include_diagrams: bool = True


class AdminNotification(BaseModel):
    project_id: uuid.UUID
    project_name: str
    user_email: str
    action: str
    timestamp: datetime
    changes_summary: Optional[str] = None