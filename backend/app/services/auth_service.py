"""
Authentication service for user management and login operations.
"""

from datetime import datetime
from typing import Optional, Union
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.auth_utils import AuthUtils
from app import schemas


class AuthService:
    """Service class for authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username/email and password.
        
        Args:
            username: Username or email
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        # Try to find user by username or email
        user = self.db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not AuthUtils.verify_password(password, user.hashed_password):
            return None
        
        # Update last login timestamp
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def create_user(self, user_data: schemas.UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user object
            
        Raises:
            HTTPException: If username/email already exists or validation fails
        """
        # Validate password strength
        password_errors = AuthUtils.validate_password_strength(user_data.password)
        if password_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {'; '.join(password_errors)}"
            )
        
        # Check if username already exists
        if self.db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        if self.db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate role
        try:
            role = UserRole(user_data.role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {[r.value for r in UserRole]}"
            )
        
        # Create user
        hashed_password = AuthUtils.get_password_hash(user_data.password)
        
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=role,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User's database ID
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: Email to search for
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, user_id: int, user_data: schemas.UserUpdate) -> User:
        """
        Update user information.
        
        Args:
            user_id: User's database ID
            user_data: Updated user data
            
        Returns:
            Updated user object
            
        Raises:
            HTTPException: If user not found or validation fails
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields if provided
        if user_data.username is not None:
            # Check if new username is already taken by another user
            existing_user = self.db.query(User).filter(
                User.username == user_data.username,
                User.id != user_id
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            user.username = user_data.username
        
        if user_data.email is not None:
            # Check if new email is already taken by another user
            existing_user = self.db.query(User).filter(
                User.email == user_data.email,
                User.id != user_id
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken"
                )
            user.email = user_data.email
        
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.role is not None:
            try:
                role = UserRole(user_data.role)
                user.role = role
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid role. Must be one of: {[r.value for r in UserRole]}"
                )
        
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Change user's password.
        
        Args:
            user_id: User's database ID
            current_password: Current password for verification
            new_password: New password
            
        Returns:
            True if password changed successfully
            
        Raises:
            HTTPException: If user not found, current password wrong, or validation fails
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not AuthUtils.verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password strength
        password_errors = AuthUtils.validate_password_strength(new_password)
        if password_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {'; '.join(password_errors)}"
            )
        
        # Update password
        user.hashed_password = AuthUtils.get_password_hash(new_password)
        self.db.commit()
        
        return True
    
    def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: User's database ID
            
        Returns:
            True if user deactivated successfully
            
        Raises:
            HTTPException: If user not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        self.db.commit()
        
        return True
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Get all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of user objects
        """
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def create_admin_user(self, username: str, email: str, password: str, full_name: str = None) -> User:
        """
        Create an admin user (for initial setup).
        
        Args:
            username: Admin username
            email: Admin email
            password: Admin password
            full_name: Admin full name
            
        Returns:
            Created admin user
        """
        # Check if admin user already exists
        existing_admin = self.db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing_admin:
            return existing_admin
        
        user_data = schemas.UserCreate(
            username=username,
            email=email,
            password=password,
            full_name=full_name or "System Administrator",
            role=UserRole.ADMIN.value
        )
        
        return self.create_user(user_data)