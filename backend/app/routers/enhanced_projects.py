# backend/app/routers/enhanced_projects.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid
import os

from app.config.database import get_async_session
from app.schemas.project_schemas import Project, ProjectCreate
from app.models.project_models import Project as ProjectModel, ProjectFile
from app.models.user_models import RateCard, User
from app.utils.enhanced_ai_engine import enhanced_ai_engine
from app.utils.rag_engine import rag_engine
from app.utils.chroma_db import store_document
from app.auth.router import current_active_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/projects", tags=["projects"])


class AnsweredQuestion(BaseModel):
    question_id: str
    question: str
    answer: str


class GenerateScopeRequest(BaseModel):
    answered_questions: Optional[List[AnsweredQuestion]] = None


class ChatMessage(BaseModel):
    message: str
    current_scope: dict


@router.post("", response_model=Project)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """Create new project with enhanced RAG capabilities"""
    try:
        db_project = ProjectModel(
            **project_data.dict(),
            owner_id=user.id
        )
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        
        # Store in knowledge base
        project_context = f"{project_data.name} {project_data.domain} {project_data.use_cases}"
        await store_document(
            document=project_context,
            metadata={
                "project_id": str(db_project.id),
                "type": "project_initial",
                "domain": project_data.domain,
                "complexity": project_data.complexity
            }
        )
        
        return db_project
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/upload-files")
async def upload_project_files(
    project_id: uuid.UUID,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """Upload and process project documents with RAG"""
    try:
        result = await db.execute(
            select(ProjectModel).where(
                ProjectModel.id == project_id,
                ProjectModel.owner_id == user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        uploaded_files = []
        extracted_content = []
        
        for file in files:
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")
            contents = await file.read()
            
            with open(file_path, "wb") as f:
                f.write(contents)
            
            text_content = await extract_text_from_file(file_path, file.filename)
            if text_content:
                extracted_content.append(text_content)
            
            db_file = ProjectFile(
                project_id=project_id,
                file_name=file.filename,
                file_path=file_path
            )
            db.add(db_file)
            uploaded_files.append({
                "filename": file.filename,
                "path": file_path
            })
        
        await db.commit()
        
        if extracted_content:
            combined_content = "\n\n".join(extracted_content)
            await store_document(
                document=combined_content,
                metadata={
                    "project_id": str(project_id),
                    "type": "uploaded_documents",
                    "domain": project.domain
                }
            )
        
        return {
            "message": "Files uploaded and processed successfully",
            "files": uploaded_files,
            "content_extracted": len(extracted_content) > 0
        }
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/analyze-with-rag")
async def analyze_project_with_rag(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """Enhanced project analysis with RAG"""
    try:
        result = await db.execute(
            select(ProjectModel).where(
                ProjectModel.id == project_id,
                ProjectModel.owner_id == user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        files_result = await db.execute(
            select(ProjectFile).where(ProjectFile.project_id == project_id)
        )
        files = files_result.scalars().all()
        
        uploaded_content = []
        for file in files:
            content = await extract_text_from_file(file.file_path, file.file_name)
            if content:
                uploaded_content.append(content)
        
        combined_content = "\n\n".join(uploaded_content) if uploaded_content else None
        
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
        
        analysis_result = await enhanced_ai_engine.analyze_project_with_rag(
            project_data=project_data,
            uploaded_content=combined_content
        )
        
        return {
            "project_id": str(project_id),
            "questions": analysis_result.get("questions", []),
            "initial_analysis": analysis_result.get("initial_analysis", {}),
            "similar_projects": analysis_result.get("similar_projects", []),
            "rag_used": analysis_result.get("rag_used", False)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG analysis failed: {str(e)}")


@router.post("/{project_id}/generate-scope-with-rag")
async def generate_scope_with_rag(
    project_id: uuid.UUID,
    request: GenerateScopeRequest,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """Generate scope using RAG-enhanced AI"""
    try:
        result = await db.execute(
            select(ProjectModel).where(
                ProjectModel.id == project_id,
                ProjectModel.owner_id == user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        rate_cards_result = await db.execute(
            select(RateCard).where(RateCard.user_id == user.id)
        )
        rate_cards = rate_cards_result.scalars().all()
        rate_cards_data = [
            {"role_name": rc.role_name, "monthly_rate": rc.monthly_rate}
            for rc in rate_cards
        ]
        
        search_query = f"{project.name} {project.domain} {project.use_cases}"
        similar_projects_result = await rag_engine.search_similar_projects(
            query=search_query,
            filters={"domain": project.domain} if project.domain else None,
            n_results=3
        )
        
        project_data = {
            "name": project.name,
            "domain": project.domain,
            "complexity": project.complexity,
            "tech_stack": project.tech_stack,
            "use_cases": project.use_cases
        }
        
        scope = await enhanced_ai_engine.generate_scope_with_rag(
            project_data=project_data,
            answered_questions=[q.dict() for q in request.answered_questions] if request.answered_questions else None,
            similar_projects=similar_projects_result.get("similar_projects", [])
        )
        
        await rag_engine.store_project_scope(project_data, scope)
        
        return {
            "project_id": str(project_id),
            "scope": scope,
            "rag_insights": scope.get('rag_insights', {}),
            "similar_projects_used": len(similar_projects_result.get("similar_projects", []))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scope generation failed: {str(e)}")


async def extract_text_from_file(file_path: str, filename: str) -> Optional[str]:
    """Extract text from various file formats"""
    try:
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.pdf':
            import PyPDF2
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        
        elif ext in ['.docx', '.doc']:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        else:
            return None
            
    except Exception as e:
        print(f"Error extracting text from {filename}: {e}")
        return None


@router.get("", response_model=List[Project])
async def get_projects(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """Get all projects"""
    try:
        result = await db.execute(
            select(ProjectModel)
            .where(ProjectModel.owner_id == user.id)
            .order_by(ProjectModel.created_at.desc())
        )
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """Get specific project"""
    try:
        result = await db.execute(
            select(ProjectModel).where(
                ProjectModel.id == project_id,
                ProjectModel.owner_id == user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))