import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.database import AsyncSessionLocal
from app.models.user_models import User
from sqlalchemy import select
import uuid

# Use the same password hashing as fastapi-users
from fastapi_users.password import PasswordHelper

password_helper = PasswordHelper()

async def create_test_user():
    async with AsyncSessionLocal() as session:
        try:
            # Check if user exists
            result = await session.execute(
                select(User).where(User.email == "admin@example.com")
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("✅ Test user already exists")
                print("   Email: admin@example.com")
                print("   Password: password123")
                return
            
            # Create new user with proper password hashing
            hashed_password = password_helper.hash("password123")
            
            user = User(
                id=uuid.uuid4(),
                email="admin@example.com",
                username="admin",
                hashed_password=hashed_password,
                is_active=True,
                is_superuser=False,
                is_verified=True
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            print("✅ Test user created successfully!")
            print("   Email: admin@example.com")
            print("   Password: password123")
            print(f"   User ID: {user.id}")
            
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    print("Creating test user...")
    asyncio.run(create_test_user())