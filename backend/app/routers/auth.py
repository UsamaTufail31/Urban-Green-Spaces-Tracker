"""
Authentication router for login, user management, and token operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services.auth_service import AuthService
from app.auth_utils import AuthUtils
from app import schemas


router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> schemas.User:
    """
    Get current user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
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
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/login", response_model=schemas.Token)
async def login(
    login_data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    
    Args:
        login_data: Login credentials (username/email and password)
        db: Database session
        
    Returns:
        JWT token with expiration information
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token
    access_token, expires_in = AuthUtils.create_token_for_user(
        user.id, user.username, user.role.value
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in
    }


@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """
    Create a new user account (admin only).
    
    Args:
        user_data: New user information
        db: Database session
        current_user: Current authenticated admin user
        
    Returns:
        Created user information (without password)
        
    Raises:
        HTTPException: If validation fails or user already exists
    """
    auth_service = AuthService(db)
    new_user = auth_service.create_user(user_data)
    
    return new_user


@router.get("/me", response_model=schemas.User)
async def get_current_user_info(current_user: schemas.User = Depends(get_current_user)):
    """
    Get current user's information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return current_user


@router.put("/me", response_model=schemas.User)
async def update_current_user(
    user_data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Update current user's information.
    
    Args:
        user_data: Updated user information
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If validation fails
    """
    # Users can only update their own basic info, not role or active status
    limited_update = schemas.UserUpdate(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        role=None,  # Can't change own role
        is_active=None  # Can't change own active status
    )
    
    auth_service = AuthService(db)
    updated_user = auth_service.update_user(current_user.id, limited_update)
    
    return updated_user


@router.put("/change-password")
async def change_password(
    password_data: schemas.PasswordChange,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Change current user's password.
    
    Args:
        password_data: Current and new password
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If current password is wrong or validation fails
    """
    auth_service = AuthService(db)
    auth_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )
    
    return {"message": "Password changed successfully"}


@router.get("/users", response_model=List[schemas.User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """
    Get all users (admin only).
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated admin user
        
    Returns:
        List of user information
    """
    auth_service = AuthService(db)
    users = auth_service.get_all_users(skip=skip, limit=limit)
    
    return users


@router.get("/users/{user_id}", response_model=schemas.User)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """
    Get specific user by ID (admin only).
    
    Args:
        user_id: User's database ID
        db: Database session
        current_user: Current authenticated admin user
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user not found
    """
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/users/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """
    Update any user's information (admin only).
    
    Args:
        user_id: User's database ID
        user_data: Updated user information
        db: Database session
        current_user: Current authenticated admin user
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If user not found or validation fails
    """
    auth_service = AuthService(db)
    updated_user = auth_service.update_user(user_id, user_data)
    
    return updated_user


@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """
    Deactivate a user account (admin only).
    
    Args:
        user_id: User's database ID
        db: Database session
        current_user: Current authenticated admin user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If user not found or trying to deactivate self
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    auth_service = AuthService(db)
    auth_service.deactivate_user(user_id)
    
    return {"message": "User account deactivated successfully"}


@router.post("/verify-token")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Verify if a JWT token is valid.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        Token validation information
        
    Raises:
        HTTPException: If token is invalid
    """
    token_data = AuthUtils.verify_token(credentials.credentials)
    
    return {
        "valid": True,
        "username": token_data.get("sub"),
        "user_id": token_data.get("user_id"),
        "role": token_data.get("role"),
        "expires": token_data.get("exp")
    }


@router.post("/refresh-token", response_model=schemas.Token)
async def refresh_token(
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Refresh JWT token for current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        New JWT token with expiration information
    """
    # Create new token
    access_token, expires_in = AuthUtils.create_token_for_user(
        current_user.id, current_user.username, current_user.role
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in
    }