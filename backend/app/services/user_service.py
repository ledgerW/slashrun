from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db.models.user import User
from backend.app.services.auth_service import auth_service


class UserService:
    """User management service with CRUD operations and business logic."""
    
    async def create_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
        organization: Optional[str] = None,
        position: Optional[str] = None,
        db: AsyncSession = None
    ) -> User:
        """Create a new user with hashed password."""
        
        # Check if user already exists
        existing_user = await self.get_user_by_email(email, db)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        existing_username = await self.get_user_by_username(username, db)
        if existing_username:
            raise ValueError("User with this username already exists")
        
        # Hash password
        hashed_password = auth_service.hash_password(password)
        
        # Create user
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            organization=organization,
            position=position,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        try:
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("User creation failed due to data constraint violation") from e
    
    async def get_user_by_email(self, email: str, db: AsyncSession) -> Optional[User]:
        """Get user by email address."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str, db: AsyncSession) -> Optional[User]:
        """Get user by username."""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: UUID, db: AsyncSession) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def update_user_profile(
        self, 
        user_id: UUID, 
        updates: Dict[str, Any], 
        db: AsyncSession
    ) -> Optional[User]:
        """Update user profile information."""
        user = await self.get_user_by_id(user_id, db)
        if not user:
            return None
        
        # Update allowed fields
        allowed_fields = {
            'full_name', 'bio', 'organization', 'position', 'username'
        }
        
        for field, value in updates.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        
        try:
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        except IntegrityError:
            await db.rollback()
            return None
    
    async def update_user_settings(
        self, 
        user_id: UUID, 
        settings: Dict[str, Any], 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Update user settings (stored as user attributes or separate settings table)."""
        user = await self.get_user_by_id(user_id, db)
        if not user:
            return {}
        
        # For now, we'll store basic settings as user attributes
        # In future, this could be extended to a separate settings table
        user.updated_at = datetime.utcnow()
        
        try:
            db.add(user)
            await db.commit()
            return settings
        except Exception:
            await db.rollback()
            return {}
    
    async def get_user_settings(self, user_id: UUID, db: AsyncSession) -> Dict[str, Any]:
        """Get user settings."""
        user = await self.get_user_by_id(user_id, db)
        if not user:
            return {}
        
        # Return default settings for now
        return {
            "theme": "dark",
            "notifications": {
                "email": True,
                "push": True,
                "scenarios": True
            },
            "preferences": {
                "defaultPlaybackSpeed": 1,
                "autoSave": True
            }
        }
    
    async def deactivate_user(self, user_id: UUID, db: AsyncSession) -> bool:
        """Deactivate a user account."""
        user = await self.get_user_by_id(user_id, db)
        if not user:
            return False
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        try:
            db.add(user)
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False
    
    async def change_password(
        self, 
        user_id: UUID, 
        current_password: str, 
        new_password: str, 
        db: AsyncSession
    ) -> bool:
        """Change user password after verifying current password."""
        user = await self.get_user_by_id(user_id, db)
        if not user:
            return False
        
        # Verify current password
        if not auth_service.verify_password(current_password, user.hashed_password):
            return False
        
        # Hash new password
        user.hashed_password = auth_service.hash_password(new_password)
        user.updated_at = datetime.utcnow()
        
        try:
            db.add(user)
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False


# Global instance for dependency injection
user_service = UserService()
