# backend/app/models/user_models.py
from sqlalchemy import Column, String, DateTime, Float, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.config.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Company(Base):
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    currency = Column(String(10), default="USD")
    owner_id = Column(UUID(as_uuid=True))


class RateCard(Base):
    __tablename__ = "rate_cards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True))
    user_id = Column(UUID(as_uuid=True))
    role_name = Column(String(100), nullable=False)
    monthly_rate = Column(Float, nullable=False)