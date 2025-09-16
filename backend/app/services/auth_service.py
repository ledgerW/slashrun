from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.config import settings
from db.models.user import User


class AuthService:
    """Authentication service for password hashing and JWT token management."""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except JWTError:
            return None
    
    async def authenticate_user(self, email: str, password: str, db: AsyncSession) -> Optional[User]:
        """Authenticate a user by email and password."""
        # Get user by email
        result = await db.execute(select(User).where(User.email == email, User.is_active == True))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Verify password
        if not self.verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def get_user_by_token(self, token: str, db: AsyncSession) -> Optional[User]:
        """Get user by JWT token."""
        payload = self.decode_token(token)
        if not payload:
            return None
        
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        
        try:
            user_id = UUID(user_id_str)
        except (ValueError, TypeError):
            return None
        
        result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
        user = result.scalar_one_or_none()
        return user
    
    async def update_last_login(self, user_id: UUID, db: AsyncSession) -> None:
        """Update user's last login timestamp and increment login count."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user:
            user.last_login_at = datetime.utcnow()
            user.login_count += 1
            user.updated_at = datetime.utcnow()
            db.add(user)
            await db.commit()


# Global instance for dependency injection
auth_service = AuthService()
