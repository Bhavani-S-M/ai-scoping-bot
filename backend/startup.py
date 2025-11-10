# backend/startup.py
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.rag_engine import rag_engine
from app.config.database import AsyncSessionLocal
from app.models.user_models import User
from sqlalchemy import select, delete
import uuid

# Import passlib - same as fastapi-users uses
from passlib.context import CryptContext

# Create password context - MUST match fastapi-users
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def initialize_system():
    """Initialize system on startup"""
    print("=" * 60)
    print("🚀 Initializing AI Scoping Bot System")
    print("=" * 60)
    
    # Initialize RAG knowledge base
    print("\n📚 Step 1: Loading Knowledge Base...")
    try:
        await rag_engine.initialize_knowledge_base()
    except Exception as e:
        print(f"⚠️ Knowledge base initialization warning: {e}")
    
    # Create demo user if doesn't exist
    print("\n👤 Step 2: Setting up Demo User...")
    async with AsyncSessionLocal() as session:
        try:
            # Check if user exists
            result = await session.execute(
                select(User).where(User.email == "demo@example.com")
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                # Delete and recreate to ensure correct password
                print("   🔄 Resetting demo user...")
                await session.execute(
                    delete(User).where(User.email == "demo@example.com")
                )
                await session.commit()
            
            # Create user with properly hashed password
            hashed_password = pwd_context.hash("demo123")
            
            demo_user = User(
                id=uuid.uuid4(),
                username="demo_user",
                email="demo@example.com",
                hashed_password=hashed_password,
                is_active=True,
                is_verified=True,
                is_superuser=False
            )
            session.add(demo_user)
            await session.commit()
            
            print("✅ Demo user created successfully")
            print("   📧 Email: demo@example.com")
            print("   🔑 Password: demo123")
            print(f"   🔐 Hash: {hashed_password[:50]}...")
                
        except Exception as e:
            print(f"❌ Error setting up demo user: {e}")
            await session.rollback()
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✨ System Initialization Complete!")
    print("🌐 Backend: http://localhost:8001")
    print("📚 API Docs: http://localhost:8001/docs")
    print("🎨 Frontend: http://localhost:5173")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    asyncio.run(initialize_system())