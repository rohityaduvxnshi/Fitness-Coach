"""
Exercise library and analytics routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.config.database import get_db
from app.models.models import (
    User, Exercise, ExerciseCategory, MuscleGroup, ExercisePR
)
from app.schemas.schemas import (
    ExerciseResponse, ExerciseCreate, ExerciseUpdate,
    ExerciseCategoryResponse, MuscleGroupResponse,
    ExercisePRResponse, ExerciseAnalyticsResponse, AnalyticsSummaryResponse
)
from app.routers.user_routes import get_current_user
from app.services.analytics import AnalyticsCalculator

router = APIRouter(prefix="/exercises", tags=["exercises"])


# ============================================================================
# EXERCISE LIBRARY ENDPOINTS
# ============================================================================

@router.get("", response_model=list[ExerciseResponse])
async def list_exercises(
    category: str = Query(None),
    muscle_group: str = Query(None),
    difficulty: str = Query(None),
    equipment: str = Query(None),
    is_active: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List exercises with optional filtering"""
    
    query = db.query(Exercise).filter(Exercise.is_active == is_active)
    
    if category:
        query = query.join(ExerciseCategory).filter(ExerciseCategory.name == category)
    
    if difficulty:
        query = query.filter(Exercise.difficulty == difficulty)
    
    if equipment:
        query = query.filter(Exercise.equipment == equipment)
    
    exercises = query.offset(skip).limit(limit).all()
    
    return [ExerciseResponse.from_orm(e) for e in exercises]


@router.post("", response_model=ExerciseResponse)
async def create_exercise(
    exercise: ExerciseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new exercise (admin only - for now, any user)"""
    
    # Check if exercise with same slug exists
    existing = db.query(Exercise).filter(Exercise.slug == exercise.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exercise with this slug already exists"
        )
    
    new_exercise = Exercise(**exercise.dict())
    
    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    
    return ExerciseResponse.from_orm(new_exercise)


@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(
    exercise_id: int,
    db: Session = Depends(get_db)
):
    """Get exercise details"""
    
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    
    return ExerciseResponse.from_orm(exercise)


@router.put("/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(
    exercise_id: int,
    exercise_update: ExerciseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an exercise"""
    
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    
    # Update only provided fields
    update_data = exercise_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exercise, field, value)
    
    db.commit()
    db.refresh(exercise)
    
    return ExerciseResponse.from_orm(exercise)


@router.delete("/{exercise_id}")
async def delete_exercise(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete an exercise (mark inactive)"""
    
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    
    exercise.is_active = False
    db.commit()
    
    return {"message": "Exercise deleted"}


# ============================================================================
# EXERCISE HISTORY & ANALYTICS
# ============================================================================

@router.get("/{exercise_id}/history", response_model=ExerciseAnalyticsResponse)
async def get_exercise_history(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's history and analytics for specific exercise"""
    
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    
    pr_data = AnalyticsCalculator.get_exercise_prs(db, current_user.id, exercise_id)
    
    # Determine trend (would need more data for true trend analysis)
    trend = "stable"  # placeholder
    
    return ExerciseAnalyticsResponse(
        exercise_id=exercise_id,
        exercise_name=exercise.name,
        total_sessions=pr_data["total_sessions"],
        heaviest_weight_kg=pr_data["heaviest_weight_kg"],
        best_estimated_1rm=pr_data["best_estimated_1rm"],
        best_reps=pr_data["best_reps"],
        best_volume_kg=pr_data["best_volume_kg"],
        recent_volume_kg=None,  # Would calculate from recent sessions
        trend=trend,
        last_session_date=pr_data["heaviest_weight_date"]
    )


@router.get("/{exercise_id}/prs", response_model=ExercisePRResponse)
async def get_exercise_prs(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all PRs for an exercise"""
    
    pr_data = AnalyticsCalculator.get_exercise_prs(db, current_user.id, exercise_id)
    
    return ExercisePRResponse(
        id=0,  # Placeholder
        user_id=current_user.id,
        exercise_id=exercise_id,
        **pr_data
    )


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/analytics/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    days: int = Query(30, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive user analytics"""
    
    analytics = AnalyticsCalculator.get_user_analytics(db, current_user.id, days)
    
    # Get recent PRs
    pr_exercises = db.query(ExercisePR).filter(
        ExercisePR.user_id == current_user.id
    ).order_by(ExercisePR.last_logged_date.desc()).limit(5).all()
    
    prs = [ExercisePRResponse.from_orm(pr) for pr in pr_exercises]
    
    return AnalyticsSummaryResponse(
        total_workouts=analytics["total_workouts"],
        total_volume_all_time=analytics["total_volume_all_time"],
        average_workout_volume=analytics["average_workout_volume"],
        weekly_frequency=analytics["weekly_frequency"],
        current_streak=analytics["current_streak"],
        personal_records=prs
    )


@router.get("/analytics/prs", response_model=list[ExercisePRResponse])
async def get_all_prs(
    limit: int = Query(50, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all personal records for user"""
    
    prs = db.query(ExercisePR).filter(
        ExercisePR.user_id == current_user.id
    ).order_by(
        ExercisePR.last_logged_date.desc()
    ).limit(limit).all()
    
    return [ExercisePRResponse.from_orm(pr) for pr in prs]


@router.get("/analytics/volume", response_model=dict)
async def get_volume_analytics(
    days: int = Query(7, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get volume analytics by muscle group"""
    
    volume_by_muscle = AnalyticsCalculator.get_muscle_group_volume(db, current_user.id, days)
    
    return {
        "period_days": days,
        "volume_by_muscle_group": volume_by_muscle
    }


@router.get("/analytics/adherence", response_model=dict)
async def get_adherence_analytics(
    days: int = Query(30, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get workout adherence metrics"""
    
    analytics = AnalyticsCalculator.get_user_analytics(db, current_user.id, days)
    
    # Simple adherence calculation
    target_workouts = 4  # assuming 4 workouts per week
    weeks = max(1, days // 7)
    target_per_period = target_workouts * weeks
    adherence_rate = (analytics["total_workouts"] / target_per_period * 100) if target_per_period > 0 else 0
    
    return {
        "period_days": days,
        "total_workouts": analytics["total_workouts"],
        "weekly_frequency": analytics["weekly_frequency"],
        "current_streak": analytics["current_streak"],
        "adherence_rate_percent": min(100, adherence_rate)
    }


# ============================================================================
# CATEGORIES & MUSCLE GROUPS
# ============================================================================

@router.get("/categories", response_model=list[ExerciseCategoryResponse])
async def list_categories(db: Session = Depends(get_db)):
    """List all exercise categories"""
    
    categories = db.query(ExerciseCategory).all()
    return [ExerciseCategoryResponse.from_orm(c) for c in categories]


@router.get("/muscle-groups", response_model=list[MuscleGroupResponse])
async def list_muscle_groups(db: Session = Depends(get_db)):
    """List all muscle groups"""
    
    muscle_groups = db.query(MuscleGroup).all()
    return [MuscleGroupResponse.from_orm(mg) for mg in muscle_groups]
