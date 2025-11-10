#backend/app/routers/knowledge_base.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from typing import List

from app.config.database import get_async_session
from app.utils.rag_engine import rag_engine
from app.auth.router import current_active_user

router = APIRouter()

@router.post("/store-project")
async def store_project_in_kb(
    project_data: dict,
    scope_data: dict,
    db: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """
    Store finalized project in knowledge base for future learning
    """
    try:
        await rag_engine.store_project_scope(
            project_data=project_data,
            scope_data=scope_data
        )
        
        return {
            "message": "Project stored in knowledge base successfully",
            "project_id": project_data.get('id'),
            "learning_status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge base storage failed: {str(e)}")

@router.get("/similar-projects")
async def find_similar_projects(
    query: str,
    domain: str = None,
    n_results: int = 5,
    db: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """
    Find similar projects from knowledge base
    """
    try:
        similar_projects = await rag_engine.search_similar_projects(
            query=query,
            filters={"domain": domain} if domain else None,
            n_results=n_results
        )
        
        return similar_projects
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similar projects search failed: {str(e)}")