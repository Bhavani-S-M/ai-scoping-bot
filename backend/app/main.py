# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.database import engine, Base
from app.models import user_models, project_models
from app.routers.enhanced_projects_v2 import router as enhanced_projects_router
from app.routers.exports import router as exports_router
from app.routers.blob import router as blob_router
from app.routers.ratecards import router as ratecards_router
from app.routers.project_prompts import router as project_prompts_router
from app.auth.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created")
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="AI-Powered Project Scoping Bot",
    description="Intelligent project scoping assistant with RAG and Real-time Refinement",
    version="3.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(enhanced_projects_router, prefix="/api")
app.include_router(exports_router, prefix="/api")
app.include_router(blob_router, prefix="/api")
app.include_router(ratecards_router, prefix="/api")
app.include_router(project_prompts_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "AI Scoping Bot API", "version": "3.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "3.0.0"}