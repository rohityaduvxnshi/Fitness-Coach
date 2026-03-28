#!/usr/bin/env python3
"""Test goal creation endpoint to see the actual error"""

import requests
import traceback
from app.config.database import SessionLocal, engine
from app.models.models import Base, User, Profile
from app.utils.jwt_handler import create_access_token
from app.routers.fitness_routes import create_goal
from app.schemas.schemas import GoalCreate
from fastapi import Depends
from sqlalchemy.orm import Session

# Create tables
Base.metadata.create_all(bind=engine)

# Create test user and profile
db = SessionLocal()

try:
    # Check if user exists
    user = db.query(User).filter(User.id == 13).first()
    if not user:
        print("User not found")
    else:
        print(f"User found: {user.email}")
        
    # Check if profile exists
    profile = db.query(Profile).filter(Profile.user_id == 13).first()
    if not profile:
        print("Profile not found")
    else:
        print(f"Profile found: Name={profile.name}, Age={profile.age}, Sex={profile.sex}, Height={profile.height_cm}, Weight={profile.weight_kg}, BF%={profile.body_fat_percentage}")
        
    # Try to call create_goal directly
    print("\nTrying to create goal...")
    goal_data = GoalCreate(goal_type="weight_loss", activity_level="moderate")
    result = create_goal(goal_data, user, db)
    print(f"Success: {result}")
    
except Exception as e:
    print(f"\nError occurred: {type(e).__name__}: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()

finally:
    db.close()
