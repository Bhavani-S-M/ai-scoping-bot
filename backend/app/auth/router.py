#backend/app/auth/router.py
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from pydantic import BaseModel
from app.models.user_models import User
from app.auth.manager import get_user_manager
from app.schemas.user_schemas import UserRead, UserCreate, UserUpdate
from app.config.config import settings

SECRET = settings.SECRET_KEY

bearer_transport = BearerTransport(tokenUrl="api/auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

router = APIRouter()

# Auth routes
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# Registration route
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# User management routes
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Custom login schema that accepts email
class LoginRequest(BaseModel):
    email: str
    password: str

# Custom login endpoint with better error handling
@router.post("/auth/login")
async def login(
    login_data: LoginRequest,
    user_manager = Depends(get_user_manager)
):
    """Custom login endpoint with enhanced error handling"""
    try:
        print(f"🔐 Login attempt for: {login_data.email}")
        
        # Authenticate using email and password
        user = await user_manager.authenticate({
            "username": login_data.email,  # UserManager.authenticate expects 'username' key
            "password": login_data.password
        })
        
        if user is None:
            print(f"❌ Login failed: Invalid credentials for {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        
        if not user.is_active:
            print(f"❌ Login failed: User {login_data.email} is not active")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is not active",
            )
        
        # Generate token using JWT strategy
        jwt_strategy = get_jwt_strategy()
        token = await jwt_strategy.write_token(user)
        
        print(f"✅ Login successful for: {user.email}")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": str(user.id),
            "email": user.email,
            "username": user.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

# Health check endpoint
@router.get("/auth/health")
async def auth_health():
    return {"status": "healthy", "service": "authentication"}

# Current user dependency
current_active_user = fastapi_users.current_user(active=True)