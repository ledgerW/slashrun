from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text


class User(SQLModel, table=True):
    """Database model for users - authentication and profile management."""
    
    __tablename__ = "users"
    
    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    # Authentication credentials
    email: str = Field(max_length=255, unique=True, index=True)
    username: str = Field(max_length=100, unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    
    # Profile information
    full_name: Optional[str] = Field(default=None, max_length=255)
    bio: Optional[str] = Field(default=None, sa_column=Column(Text))
    organization: Optional[str] = Field(default=None, max_length=255)
    position: Optional[str] = Field(default=None, max_length=255)
    
    # Account status and activity
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    login_count: int = Field(default=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = Field(default=None)
    
    class Config:
        """SQLModel configuration."""
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "user123",
                "full_name": "John Doe",
                "organization": "Example Corp",
                "position": "Analyst"
            }
        }
