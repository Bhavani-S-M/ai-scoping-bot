# backend/app/auth/manager.py
import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_models import User
from app.config.config import settings
from app.config.database import get_async_session

SECRET = settings.SECRET_KEY

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
    
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"✅ User {user.id} has registered.")
    
    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"🔑 User {user.id} has forgot their password. Reset token: {token}")
    
    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"📧 Verification requested for user {user.id}. Verification token: {token}")
    
    # Add custom authentication with debugging
    async def authenticate(self, credentials):
        """Custom authenticate method with detailed logging"""
        try:
            print(f"🔍 Authentication attempt for: {credentials.get('username')}")
            
            # Get user from database
            user = await self.get_by_email(credentials.get('username'))
            
            if user is None:
                print(f"❌ User not found: {credentials.get('username')}")
                return None
            
            print(f"✅ User found: {user.email}, Active: {user.is_active}")
            
            # Verify password
            verified, updated_password_hash = self.password_helper.verify_and_update(
                credentials.get('password'), user.hashed_password
            )
            
            if not verified:
                print(f"❌ Password verification failed for: {user.email}")
                print(f"   Stored hash: {user.hashed_password[:50]}...")
                return None
            
            print(f"✅ Password verified successfully for: {user.email}")
            
            # Update password hash if needed
            if updated_password_hash is not None:
                print(f"🔄 Updating password hash for: {user.email}")
                await self.user_db.update(user, {"hashed_password": updated_password_hash})
            
            return user
            
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)