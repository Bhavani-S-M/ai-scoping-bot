import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user_models import User
from app.config.database import AsyncSessionLocal

async def create_demo_user():
    """Create a demo user for testing"""
    async with AsyncSessionLocal() as session:
        # Check if demo user already exists
        result = await session.execute(
            select(User).where(User.id == uuid.UUID("4628bfc3-8625-4791-811f-5b837954cd30"))
        )
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            demo_user = User(
                id=uuid.UUID("4628bfc3-8625-4791-811f-5b837954cd30"),
                username="demo_user",
                email="demo@example.com",
                hashed_password="demo_password_hash",  # Add dummy password
                is_active=True,
                is_verified=True
            )
            session.add(demo_user)
            await session.commit()
            print("✅ Demo user created")
        else:
            print("✅ Demo user already exists")

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_demo_user())