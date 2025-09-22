"""
Authentication dependencies and middleware for protecting routes.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.auth_service import AuthService
from app.auth_utils import AuthUtils
from app import schemas
from app.models.user import UserRole


security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[schemas.User]:
    """
    Get current user from JWT token (optional - returns None if no token).
    
    Args:
        credentials: HTTP Bearer token credentials (optional)
        db: Database session
        
    Returns:
        Current user object or None
    """
    if not credentials:
        return None
    
    try:
        # Verify token
        token_data = AuthUtils.verify_token(credentials.credentials)
        
        # Get user from database
        auth_service = AuthService(db)
        user = auth_service.get_user_by_username(token_data.get("sub"))
        
        if user is None or not user.is_active:
            return None
        
        return user
    except HTTPException:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> schemas.User:
    """
    Get current user from JWT token (required).
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token
    token_data = AuthUtils.verify_token(credentials.credentials)
    
    # Get user from database
    auth_service = AuthService(db)
    user = auth_service.get_user_by_username(token_data.get("sub"))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated"
        )
    
    return user


async def get_admin_user(current_user: schemas.User = Depends(get_current_user)) -> schemas.User:
    """
    Dependency to ensure current user is an admin.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_active_user(current_user: schemas.User = Depends(get_current_user)) -> schemas.User:
    """
    Dependency to ensure current user is active (for general authenticated routes).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if active
        
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated"
        )
    return current_user


def create_permission_dependency(required_role: UserRole):
    """
    Factory function to create role-based permission dependencies.
    
    Args:
        required_role: Required user role
        
    Returns:
        Dependency function for the specified role
    """
    async def permission_dependency(current_user: schemas.User = Depends(get_current_user)) -> schemas.User:
        if UserRole(current_user.role) != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role.value}"
            )
        return current_user
    
    return permission_dependency


# Common permission dependencies
require_admin = create_permission_dependency(UserRole.ADMIN)
require_viewer = create_permission_dependency(UserRole.VIEWER)


def check_user_permission(current_user: schemas.User, required_role: UserRole) -> bool:
    """
    Check if user has the required role permission.
    
    Args:
        current_user: Current user
        required_role: Required role
        
    Returns:
        True if user has permission, False otherwise
    """
    try:
        user_role = UserRole(current_user.role)
        # Admin has access to everything
        if user_role == UserRole.ADMIN:
            return True
        # Check specific role
        return user_role == required_role
    except ValueError:
        return False


def check_admin_permission(current_user: schemas.User) -> bool:
    """
    Check if user has admin permissions.
    
    Args:
        current_user: Current user
        
    Returns:
        True if user is admin, False otherwise
    """
    return check_user_permission(current_user, UserRole.ADMIN)


class AuthMiddleware:
    """Authentication middleware for additional security features."""
    
    @staticmethod
    def verify_token_not_expired(token: str) -> bool:
        """
        Verify that a token is not expired.
        
        Args:
            token: JWT token string
            
        Returns:
            True if token is valid and not expired
        """
        return not AuthUtils.is_token_expired(token)
    
    @staticmethod
    def extract_user_info_from_token(token: str) -> dict:
        """
        Extract user information from JWT token without full verification.
        
        Args:
            token: JWT token string
            
        Returns:
            Dictionary with user information
        """
        try:
            return AuthUtils.verify_token(token)
        except HTTPException:
            return {}
    
    @staticmethod
    def validate_admin_operation(current_user: schemas.User, operation: str) -> bool:
        """
        Validate if user can perform admin operations.
        
        Args:
            current_user: Current user
            operation: Operation being performed
            
        Returns:
            True if operation is allowed
            
        Raises:
            HTTPException: If operation is not allowed
        """
        if not check_admin_permission(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Admin access required for operation: {operation}"
            )
        return True