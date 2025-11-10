#backend/app/config/database.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from fastapi import Depends
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Async SQLAlchemy engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base model
Base = declarative_base()


# Dependency for FastAPI
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# User database dependency - Import User INSIDE the function to avoid circular import
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    from fastapi_users.db import SQLAlchemyUserDatabase
    from app.models.user_models import User  # Import here, not at top
    yield SQLAlchemyUserDatabase(session, User)