from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from app.config.database import get_db
from app.config.settings import settings
from app.models.models import User
from app.schemas.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.utils.password_hash import hash_password, verify_password
from app.utils.jwt_handler import create_access_token

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    Request:
        email: str (valid email format)
        password: str (minimum 6 characters)
    
    Response:
        201: User created successfully
        400: Email already registered or validation error
        422: Invalid input data
    """
    # Normalize email
    normalized_email = user_data.email.lower().strip()
    logger.info(f"[AUTH] Registration attempt for email: {normalized_email}")
    
    try:
        # Validate email format (basic validation - Pydantic EmailStr does more)
        if not normalized_email or "@" not in normalized_email or "." not in normalized_email.split("@")[-1]:
            logger.warning(f"[AUTH] Invalid email format: {normalized_email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Validate password length
        if len(user_data.password) < 6:
            logger.warning(f"[AUTH] Password too short for email: {normalized_email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters"
            )
        
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == normalized_email).first()
        
        if existing_user:
            logger.warning(f"[AUTH] Registration failed - email already exists: {normalized_email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        new_user = User(
            email=normalized_email,
            password_hash=hash_password(user_data.password)
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"[AUTH] Registration successful - user created: {new_user.id} ({new_user.email})")
        
        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[AUTH] Registration failed with exception: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to server error"
        )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return JWT token
    
    Request:
        email: str (valid email format)
        password: str (user's password)
    
    Response:
        200: Login successful with JWT token
        401: Invalid credentials
        403: User account is disabled
    """
    # Normalize email
    normalized_email = user_data.email.lower().strip()
    logger.info(f"[AUTH] Login attempt for email: {normalized_email}")
    
    try:
        # Find user by email
        user = db.query(User).filter(User.email == normalized_email).first()
        
        if not user:
            logger.warning(f"[AUTH] Login failed - user not found: {normalized_email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Verify password
        if not verify_password(user_data.password, user.password_hash):
            logger.warning(f"[AUTH] Login failed - invalid password for user: {normalized_email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"[AUTH] Login failed - user account disabled: {normalized_email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.info(f"[AUTH] Login successful - user: {user.id} ({user.email})")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[AUTH] Login failed with exception: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(db: Session = Depends(get_db)):
    """Refresh access token (placeholder)"""
    logger.info("[AUTH] Token refresh requested (not yet implemented)")
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not yet implemented"
    )
