import asyncio
import os
import sys

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config.database import get_async_session, engine
from app.models.user_models import User
from app.auth.manager import get_user_manager
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.password import PasswordHelper

async def create_demo_user():
    """Create a demo user for testing"""
    try:
        print("🔄 Creating demo user...")
        
        # Create tables first
        async with engine.begin() as conn:
            await conn.run_sync(User.metadata.create_all)
        
        # Get user manager and password helper
        user_manager = get_user_manager()
        password_helper = PasswordHelper()
        
        # Check if demo user already exists
        async for session in get_async_session():
            existing_user = await session.execute(
                User.__table__.select().where(User.email == "demo@example.com")
            )
            user = existing_user.scalar_one_or_none()
            
            if user:
                print("✅ Demo user already exists:")
                print(f"   Email: demo@example.com")
                print(f"   Password: demopassword")
                return
            
            # Create demo user
            hashed_password = password_helper.hash("demopassword")
            demo_user = User(
                email="demo@example.com",
                hashed_password=hashed_password,
                username="demo_user",
                is_active=True,
                is_verified=True,
                is_superuser=False
            )
            
            session.add(demo_user)
            await session.commit()
            
            print("✅ Demo user created successfully!")
            print(f"   Email: demo@example.com")
            print(f"   Password: demopassword")
            print("   You can now login with these credentials")
            
    except Exception as e:
        print(f"❌ Error creating demo user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_demo_user())