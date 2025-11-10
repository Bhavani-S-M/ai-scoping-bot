# backend/startup.py
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config.database import get_async_session, engine, Base
from app.models.user_models import User
from fastapi_users.password import PasswordHelper

async def create_demo_user():
    """Create demo user if not exists"""
    try:
        print("🔄 Starting demo user creation...")
        
        password_helper = PasswordHelper()
        
        # Ensure tables exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables verified")
        
        # Create demo user
        async for session in get_async_session():
            try:
                # Check if demo user exists
                result = await session.execute(
                    select(User).where(User.email == "demo@example.com")
                )
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    print("✅ Demo user already exists")
                    print(f"   Email: {existing_user.email}")
                    print(f"   Active: {existing_user.is_active}")
                    return
                
                # Create new demo user
                print("📝 Creating demo user...")
                hashed_password = password_helper.hash("demopassword")
                
                demo_user = User(
                    email="demo@example.com",
                    username="demo_user",
                    hashed_password=hashed_password,
                    is_active=True,
                    is_verified=True,
                    is_superuser=False
                )
                
                session.add(demo_user)
                await session.commit()
                await session.refresh(demo_user)
                
                print("✅ Demo user created successfully!")
                print(f"   Email: {demo_user.email}")
                print(f"   Password: demopassword")
                print(f"   Active: {demo_user.is_active}")
                
            except Exception as e:
                print(f"❌ Error creating demo user: {e}")
                await session.rollback()
                raise
            finally:
                break
                
    except Exception as e:
        print(f"❌ Fatal error in startup: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("=" * 50)
    print("DEMO USER SETUP")
    print("=" * 50)
    asyncio.run(create_demo_user())
    print("=" * 50)