#backend/app/routers/diagrams.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_async_session
from app.utils.architecture_generator import architecture_generator
from app.auth.router import current_active_user

router = APIRouter()

@router.post("/generate-architecture")
async def generate_architecture_diagram(
    project_data: dict,
    db: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """
    Generate architecture diagram for project
    """
    try:
        diagram = await architecture_generator.generate_architecture_diagram(project_data)
        return diagram
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagram generation failed: {str(e)}")

@router.post("/generate-workflow")
async def generate_workflow_diagram(
    activities: list,
    db: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """
    Generate workflow diagram from activities
    """
    try:
        diagram = await architecture_generator.generate_workflow_diagram(activities)
        return diagram
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow generation failed: {str(e)}")