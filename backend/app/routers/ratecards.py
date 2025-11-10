# backend/app/routers/ratecards.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.config.database import get_async_session
from app.models.user_models import RateCard, Company
from app.auth.router import fastapi_users
from pydantic import BaseModel
import uuid


router = APIRouter(prefix="/api/ratecards", tags=["ratecards"])
current_active_user = fastapi_users.current_user(active=True)


class RateCardCreate(BaseModel):
    company_id: uuid.UUID
    role_name: str
    monthly_rate: float


class RateCardRead(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    user_id: uuid.UUID
    role_name: str
    monthly_rate: float
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[RateCardRead])
async def get_rate_cards(
    db: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """Get all rate cards for current user"""
    try:
        result = await db.execute(
            select(RateCard).where(RateCard.user_id == user.id)
        )
        rate_cards = result.scalars().all()
        return rate_cards
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=RateCardRead)
async def create_rate_card(
    rate_card: RateCardCreate,
    db: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """Create a new rate card"""
    try:
        db_rate_card = RateCard(
            **rate_card.dict(),
            user_id=user.id
        )
        db.add(db_rate_card)
        await db.commit()
        await db.refresh(db_rate_card)
        return db_rate_card
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{rate_card_id}")
async def delete_rate_card(
    rate_card_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """Delete a rate card"""
    try:
        result = await db.execute(
            select(RateCard).where(
                RateCard.id == rate_card_id,
                RateCard.user_id == user.id
            )
        )
        rate_card = result.scalar_one_or_none()
        
        if not rate_card:
            raise HTTPException(status_code=404, detail="Rate card not found")
        
        await db.delete(rate_card)
        await db.commit()
        return {"message": "Rate card deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))