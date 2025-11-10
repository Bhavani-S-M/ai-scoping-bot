#backend/app/routers/enhanced_projects_v2.py
# backend/app/routers/enhanced_projects_v2.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid
import os

from app.config.database import get_async_session
from app.schemas.project_schemas import Project, ProjectCreate
from app.models.project_models import Project as ProjectModel, ProjectFile
from app.utils.document_parser import document_parser
from app.utils.architecture_generator import architecture_generator
from app.utils.refinement_engine import refinement_engine
from app.utils.enhanced_ai_engine import enhanced_ai_engine
from app.utils.rag_engine import rag_engine
from app.utils.chroma_db import store_document
from app.auth.router import current_active_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/projects", tags=["enhanced_projects"])


class DocumentUploadRequest(BaseModel):
    extract_entities: bool = True


class RefinementRequest(BaseModel):
    message: str
    current_scope: dict


class FinalizeRequest(BaseModel):
    scope_data: dict
    user_feedback: Optional[str] = None
    approval_status: str = "approved"


# ============================================================================
# 1. CREATE PROJECT WITH DOCUMENT UPLOAD
# ============================================================================

@router.post("/{project_id}/upload-document")
async def upload_and_parse_document(
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """
    Upload RFP/SOW/Requirements document and extract entities
    """
    try:
        # Verify project ownership
        result = await db.execute(
            select(ProjectModel).where(
                ProjectModel.id == project_id,
                ProjectModel.owner_id == user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Save file
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Parse and extract entities
        file_type = file_extension.replace('.', '')
        parsed_data = await document_parser.parse_and_extract(file_path, file_type)
        
        # Store in database
        db_file = ProjectFile(
            project_id=project_id,
            file_name=file.filename,
            file_path=file_path
        )
        db.add(db_file)
        
        # Update project with extracted entities
        entities = parsed_data['entities']
        project.domain = entities.get('domain', project.domain)
        project.complexity = entities.get('complexity', project.complexity)
        project.tech_stack = ', '.join(entities.get('tech_stack', []))
        project.use_cases = ', '.join(entities.get('key_features', []))
        project.compliance = ', '.join(entities.get('compliance_requirements', []))
        project.duration = entities.get('estimated_duration', project.duration)
        
        await db.commit()
        
        # Store in vector DB for RAG
        await store_document(
            document=parsed_data['parsed_text']['raw_text'],
            metadata={
                "project_id": str(project_id),
                "type": "uploaded_document",
                "filename": file.filename,
                "extraction_confidence": parsed_data['extraction_confidence']
            }
        )
        
        return {
            "message": "Document uploaded and processed successfully",
            "extracted_entities": entities,
            "confidence": parsed_data['extraction_confidence'],
            "project_updated": True
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 2. GENERATE COMPREHENSIVE SCOPE WITH ARCHITECTURE
# ============================================================================

@router.post("/{project_id}/generate-comprehensive-scope")
async def generate_comprehensive_scope(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """
    Generate comprehensive project scope with:
    - Full activity breakdown
    - Resource mapping
    - Timeline with milestones
    - Cost projection
    - Architecture diagram
    - Workflow diagram
    - Confidence scoring
    """
    try:
        # Get project
        result = await db.execute(
            select(ProjectModel).where(
                ProjectModel.id == project_id,
                ProjectModel.owner_id == user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Prepare project data
        project_data = {
            "id": str(project.id),
            "name": project.name,
            "domain": project.domain,
            "complexity": project.complexity,
            "tech_stack": project.tech_stack,
            "use_cases": project.use_cases,
            "compliance": project.compliance,
            "duration": project.duration
        }
        
        # Search for similar projects (RAG)
        search_query = f"{project.name} {project.domain} {project.use_cases}"
        similar_projects = await rag_engine.search_similar_projects(
            query=search_query,
            filters={"domain": project.domain} if project.domain else None,
            n_results=3
        )
        
        # Generate scope using RAG
        scope = await enhanced_ai_engine.generate_scope_with_rag(
            project_data=project_data,
            answered_questions=None,
            similar_projects=similar_projects.get("similar_projects", [])
        )
        
        # Generate architecture diagram
        architecture_diagram = await architecture_generator.generate_architecture_diagram(project_data)
        
        # Generate workflow diagram
        workflow_diagram = await architecture_generator.generate_workflow_diagram(
            scope.get('activities', [])
        )
        
        # Calculate confidence score
        confidence_score = calculate_confidence_score(
            similar_projects=similar_projects.get("similar_projects", []),
            rag_used=len(similar_projects.get("similar_projects", [])) > 0
        )
        
        # Add diagrams and metadata to scope
        scope['diagrams'] = {
            'architecture': architecture_diagram,
            'workflow': workflow_diagram
        }
        
        scope['metadata'] = {
            'confidence_score': confidence_score,
            'rag_sources_count': len(similar_projects.get("similar_projects", [])),
            'generated_at': datetime.now().isoformat(),
            'version': '2.0'
        }
        
        # Add detailed assumptions and dependencies
        scope['assumptions'] = generate_assumptions(project_data, scope)
        scope['dependencies'] = extract_dependencies(scope.get('activities', []))
        
        return {
            "project_id": str(project_id),
            "scope": scope,
            "confidence": confidence_score,
            "rag_enhanced": len(similar_projects.get("similar_projects", [])) > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 3. INTERACTIVE REFINEMENT
# ============================================================================

@router.post("/{project_id}/refine")
async def refine_scope(
    project_id: uuid.UUID,
    request: RefinementRequest,
    db: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """
    Interactive scope refinement:
    - Modify tasks/activities
    - Adjust timeline
    - Apply discounts
    - Modify resources
    - Recalculate automatically
    """
    try:
        # Process refinement
        result = await refinement_engine.process_refinement_request(
            user_message=request.message,
            current_scope=request.current_scope
        )
        
        return {
            "updated_scope": result['updated_scope'],
            "response": result['response'],
            "changes_made": result['changes_made'],
            "intent_detected": result['intent']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 4. FINALIZE AND LEARN
# ============================================================================

@router.post("/{project_id}/finalize")
async def finalize_scope(
    project_id: uuid.UUID,
    request: FinalizeRequest,
    db: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """
    Finalize scope and update knowledge base for learning
    """
    try:
        # Get project
        result = await db.execute(
            select(ProjectModel).where(
                ProjectModel.id == project_id,
                ProjectModel.owner_id == user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if request.approval_status == "approved":
            # Store finalized scope in knowledge base for future learning
            project_data = {
                "id": str(project.id),
                "name": project.name,
                "domain": project.domain,
                "complexity": project.complexity,
                "tech_stack": project.tech_stack
            }
            
            await rag_engine.store_project_scope(
                project_data=project_data,
                scope_data=request.scope_data
            )
            
            return {
                "message": "Project scope finalized and added to knowledge base",
                "project_id": str(project_id),
                "learning_status": "success",
                "feedback_recorded": request.user_feedback is not None
            }
        else:
            return {
                "message": "Project scope saved but not added to knowledge base (not approved)",
                "project_id": str(project_id),
                "learning_status": "skipped"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

from datetime import datetime

def calculate_confidence_score(similar_projects: list, rag_used: bool) -> float:
    """Calculate confidence score based on RAG matches"""
    if not rag_used or not similar_projects:
        return 0.6  # Base confidence without RAG
    
    # Average similarity scores
    avg_similarity = sum(p.get('similarity_score', 0) for p in similar_projects) / len(similar_projects)
    
    # Confidence = 0.6 base + 0.4 * average similarity
    confidence = 0.6 + (0.4 * avg_similarity)
    
    return round(confidence, 2)


def generate_assumptions(project_data: dict, scope: dict) -> list:
    """Generate key assumptions for the project"""
    assumptions = [
        "Client will provide timely feedback and approvals",
        "All required resources will be available as planned",
        "Requirements are stable and major changes will follow change management process",
        "Development environment and tools are accessible",
        "Third-party services/APIs will be available and functioning"
    ]
    
    # Add domain-specific assumptions
    domain = project_data.get('domain', '')
    if 'healthcare' in domain.lower():
        assumptions.append("HIPAA compliance requirements are clearly documented")
    if 'finance' in domain.lower():
        assumptions.append("PCI-DSS and financial compliance standards are defined")
    
    return assumptions


def extract_dependencies(activities: list) -> list:
    """Extract and organize project dependencies"""
    dependencies = []
    
    for activity in activities:
        if activity.get('dependencies'):
            dependencies.append({
                "activity": activity['name'],
                "depends_on": activity['dependencies'],
                "phase": activity.get('phase', 'Unknown')
            })
    
    return dependencies