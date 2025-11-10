# backend/test_password.py
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.database import AsyncSessionLocal
from app.models.user_models import User
from sqlalchemy import select
from passlib.context import CryptContext

# Create password context - same as fastapi-users
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def test_password():
    """Test password verification for demo user"""
    print("=" * 60)
    print("🔐 Password Verification Test")
    print("=" * 60)
    
    async with AsyncSessionLocal() as session:
        try:
            # Get demo user
            result = await session.execute(
                select(User).where(User.email == "demo@example.com")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ Demo user not found!")
                return
            
            print(f"\n✅ Demo user found:")
            print(f"   Email: {user.email}")
            print(f"   Username: {user.username}")
            print(f"   Active: {user.is_active}")
            print(f"   Verified: {user.is_verified}")
            print(f"   Hash: {user.hashed_password[:50]}...")
            
            # Test password verification
            test_password = "demopassword"
            print(f"\n🔍 Testing password: {test_password}")
            
            # Verify using passlib (same as fastapi-users)
            is_valid = pwd_context.verify(test_password, user.hashed_password)
            
            if is_valid:
                print(f"✅ Password verification SUCCESSFUL!")
            else:
                print(f"❌ Password verification FAILED!")
                
                # Try to generate a new hash and compare
                new_hash = pwd_context.hash(test_password)
                print(f"\n🔄 Generated new hash: {new_hash[:50]}...")
                print(f"   Old hash:           {user.hashed_password[:50]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_password())