from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, validator

from backend.app.core.database import get_db
from db.models.user import User
from backend.app.services.user_service import user_service
from backend.app.api.auth import get_current_user


router = APIRouter()


# Request/Response Models
class RegisterRequest(BaseModel):
    """User registration request model."""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    organization: Optional[str] = None
    position: Optional[str] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (with optional underscores and hyphens)')
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters long')
        return v
    
    @validator('password')
    def password_validation(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserProfile(BaseModel):
    """User profile response model."""
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    organization: Optional[str] = None
    position: Optional[str] = None
    is_active: bool
    created_at: str
    last_login_at: Optional[str] = None


class UserProfileUpdate(BaseModel):
    """User profile update request model."""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    organization: Optional[str] = None
    position: Optional[str] = None
    username: Optional[str] = None


class SettingsUpdate(BaseModel):
    """User settings update request model."""
    theme: Optional[str] = None
    notifications: Optional[Dict[str, bool]] = None
    preferences: Optional[Dict[str, Any]] = None


class PasswordChangeRequest(BaseModel):
    """Password change request model."""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def password_validation(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


# API Endpoints
@router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account."""
    try:
        user = await user_service.create_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
            organization=user_data.organization,
            position=user_data.position,
            db=db
        )
        
        return UserProfile(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            bio=user.bio,
            organization=user.organization,
            position=user.position,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login_at=user.last_login_at.isoformat() if user.last_login_at else None
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/profile", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile information."""
    return UserProfile(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        bio=current_user.bio,
        organization=current_user.organization,
        position=current_user.position,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
        last_login_at=current_user.last_login_at.isoformat() if current_user.last_login_at else None
    )


@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    updates: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile information."""
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update"
        )
    
    updated_user = await user_service.update_user_profile(
        user_id=current_user.id,
        updates=update_data,
        db=db
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile"
        )
    
    return UserProfile(
        id=str(updated_user.id),
        email=updated_user.email,
        username=updated_user.username,
        full_name=updated_user.full_name,
        bio=updated_user.bio,
        organization=updated_user.organization,
        position=updated_user.position,
        is_active=updated_user.is_active,
        created_at=updated_user.created_at.isoformat(),
        last_login_at=updated_user.last_login_at.isoformat() if updated_user.last_login_at else None
    )


@router.get("/settings")
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's settings."""
    settings = await user_service.get_user_settings(current_user.id, db)
    return settings


@router.put("/settings")
async def update_user_settings(
    settings: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's settings."""
    settings_data = {k: v for k, v in settings.dict().items() if v is not None}
    
    updated_settings = await user_service.update_user_settings(
        user_id=current_user.id,
        settings=settings_data,
        db=db
    )
    
    return updated_settings


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password."""
    success = await user_service.change_password(
        user_id=current_user.id,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
        db=db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    return {"message": "Password changed successfully"}


@router.delete("/account")
async def deactivate_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate user account."""
    success = await user_service.deactivate_user(current_user.id, db)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to deactivate account"
        )
    
    return {"message": "Account deactivated successfully"}
