"""
User model for authentication and authorization.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

from app.database import Base


class UserRole(enum.Enum):
    """User roles for authorization."""
    ADMIN = "admin"
    VIEWER = "viewer"


class User(Base):
    """
    User model for authentication and admin access.
    
    Attributes:
        id: Primary key
        username: Unique username for login
        email: User's email address
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        role: User role (admin or viewer)
        is_active: Whether the user account is active
        created_at: Timestamp when user was created
        last_login: Timestamp of last successful login
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive fields)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }