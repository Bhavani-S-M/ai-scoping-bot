#backend/app/auth/init.py
from .router import router, fastapi_users
from .manager import get_user_manager

__all__ = ["router", "fastapi_users", "get_user_manager"]