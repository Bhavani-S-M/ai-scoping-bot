# backend/app/routers/blob.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_async_session
from app.auth.router import fastapi_users
import os
import uuid

router = APIRouter(prefix="/api/blob", tags=["blob"])
current_active_user = fastapi_users.current_user(active=True)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """Upload a file"""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        return {
            "filename": file.filename,
            "file_path": file_path,
            "size": len(contents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{file_path}")
async def delete_file(
    file_path: str,
    db: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user)
):
    """Delete a file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))