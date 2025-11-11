# backend/app/routers/refinement.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.config.database import get_async_session
from app.schemas.project_schemas import RefinementRequest, RefinementResponse
from app.utils.refinement_engine import refinement_engine
from app.auth.router import current_active_user

router = APIRouter(prefix="/refinement", tags=["refinement"])

@router.post("/refine", response_model=RefinementResponse)
async def refine_scope(
    request: RefinementRequest,
    db: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """
    Enhanced scope refinement endpoint with real-time updates
    Handles:
    - Task modifications (add/remove/modify activities)
    - Timeline adjustments (extend/shorten duration)
    - Discount applications (percentage or flat amount)
    - Resource changes (add/remove team members)
    """
    try:
        print(f"🔧 Processing refinement request: {request.message[:100]}...")
        
        result = await refinement_engine.process_refinement_request(
            user_message=request.message,
            current_scope=request.current_scope
        )
        
        print(f"✅ Refinement completed: {len(result.get('changes_made', []))} changes made")
        
        return RefinementResponse(**result)
        
    except Exception as e:
        print(f"❌ Refinement error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")