from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database.base import get_db
from backend.models import User
from backend.schemas import UserCreate, UserUpdate, UserInDB, Token
from backend.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_active_user,
    check_user_permissions,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    timedelta
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=UserInDB)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new user.
    
    Args:
        user (UserCreate): User data
        db (Session): Database session
        current_user (User): Current authenticated user
        
    Returns:
        UserInDB: Created user
        
    Raises:
        HTTPException: If user creation fails or unauthorized
    """
    if not check_user_permissions(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        name=user.name,
        role=user.role,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information.
    
    Args:
        current_user (User): Current authenticated user
        
    Returns:
        UserInDB: Current user information
    """
    return current_user

@router.put("/me", response_model=UserInDB)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user information.
    
    Args:
        user_update (UserUpdate): Updated user data
        current_user (User): Current authenticated user
        db (Session): Database session
        
    Returns:
        UserInDB: Updated user information
    """
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/", response_model=List[UserInDB])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of users.
    
    Args:
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        db (Session): Database session
        current_user (User): Current authenticated user
        
    Returns:
        List[UserInDB]: List of users
        
    Raises:
        HTTPException: If unauthorized
    """
    if not check_user_permissions(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserInDB)
async def read_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user by ID.
    
    Args:
        user_id (str): User ID
        db (Session): Database session
        current_user (User): Current authenticated user
        
    Returns:
        UserInDB: User information
        
    Raises:
        HTTPException: If user not found or unauthorized
    """
    if not check_user_permissions(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update user information.
    
    Args:
        user_id (str): User ID
        user_update (UserUpdate): Updated user data
        db (Session): Database session
        current_user (User): Current authenticated user
        
    Returns:
        UserInDB: Updated user information
        
    Raises:
        HTTPException: If user not found or unauthorized
    """
    if not check_user_permissions(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user 