# backend/app/routers/project_prompts.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.config.database import get_async_session
from app.models.project_models import ProjectPromptHistory
from app.auth.router import fastapi_users
from pydantic import BaseModel
from datetime import datetime
import uuid


router = APIRouter(prefix="/api/project-prompts", tags=["project-prompts"])
current_active_user = fastapi_users.current_user(active=True)


class PromptCreate(BaseModel):
    project_id: uuid.UUID
    role: str
    message: str


class PromptRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    message: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/{project_id}", response_model=List[PromptRead])
async def get_project_prompts(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """Get all prompts for a specific project"""
    try:
        result = await db.execute(
            select(ProjectPromptHistory)
            .where(ProjectPromptHistory.project_id == project_id)
            .order_by(ProjectPromptHistory.created_at)
        )
        prompts = result.scalars().all()
        return prompts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=PromptRead)
async def create_prompt(
    prompt: PromptCreate,
    db: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """Create a new prompt entry"""
    try:
        db_prompt = ProjectPromptHistory(
            **prompt.dict(),
            user_id=user.id
        )
        db.add(db_prompt)
        await db.commit()
        await db.refresh(db_prompt)
        return db_prompt
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
