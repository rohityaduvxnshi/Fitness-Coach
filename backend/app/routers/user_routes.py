from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
import logging

from app.config.database import get_db
from app.models.models import User, Profile
from app.schemas.schemas import ProfileCreate, ProfileUpdate, ProfileResponse, UserResponse
from app.utils.jwt_handler import decode_access_token

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user from Bearer token in Authorization header"""
    
    # Validate header exists
    if not authorization:
        logger.warning("[USERS] Missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    # Validate Bearer format
    if not authorization.startswith("Bearer "):
        logger.warning(f"[USERS] Invalid Authorization header format: {authorization[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    # Extract token
    try:
        token = authorization.split(" ", 1)[1]
    except IndexError:
        logger.warning("[USERS] Malformed Bearer token (no token after 'Bearer')")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed bearer token"
        )
    
    # Decode token
    token_data = decode_access_token(token)
    
    if token_data is None:
        logger.warning("[USERS] Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Fetch user
    user = db.query(User).filter(User.id == token_data["user_id"]).first()
    
    if user is None:
        logger.warning(f"[USERS] User not found for token_data: {token_data}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        logger.warning(f"[USERS] User account inactive: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.post("/profile", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update user profile"""
    
    # Check if profile already exists
    existing_profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PUT to update."
        )
    
    # Create new profile
    new_profile = Profile(
        user_id=current_user.id,
        name=profile_data.name,
        age=profile_data.age,
        sex=profile_data.sex,
        height_cm=profile_data.height_cm,
        weight_kg=profile_data.weight_kg,
        body_fat_percentage=profile_data.body_fat_percentage
    )
    
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    
    return new_profile


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile"""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return profile


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Update only provided fields
    if profile_data.name is not None:
        profile.name = profile_data.name
    if profile_data.age is not None:
        profile.age = profile_data.age
    if profile_data.sex is not None:
        profile.sex = profile_data.sex
    if profile_data.height_cm is not None:
        profile.height_cm = profile_data.height_cm
    if profile_data.weight_kg is not None:
        profile.weight_kg = profile_data.weight_kg
    if profile_data.body_fat_percentage is not None:
        profile.body_fat_percentage = profile_data.body_fat_percentage
    
    db.commit()
    db.refresh(profile)
    
    return profile
