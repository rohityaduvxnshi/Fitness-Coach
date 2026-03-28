"""
Workout execution and management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.config.database import get_db
from app.models.models import (
    User, Workout, WorkoutExercise, Set, Exercise
)
from app.schemas.schemas import (
    WorkoutResponse, WorkoutStart, WorkoutFinish, 
    WorkoutExerciseResponse, WorkoutExerciseCreate,
    SetResponse, SetCreate, SetUpdate
)
from app.routers.user_routes import get_current_user
from app.services.analytics import AnalyticsCalculator

router = APIRouter(prefix="/workouts", tags=["workouts"])


# ============================================================================
# WORKOUT SESSION ENDPOINTS
# ============================================================================

@router.post("/start", response_model=WorkoutResponse)
async def start_workout(
    workout_start: WorkoutStart,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new workout session"""
    
    workout = Workout(
        user_id=current_user.id,
        goal_id=workout_start.goal_id,
        name=workout_start.name,
        notes=workout_start.notes,
        started_at=datetime.utcnow()
    )
    
    db.add(workout)
    db.commit()
    db.refresh(workout)
    
    return WorkoutResponse.from_orm(workout)


@router.get("/active", response_model=WorkoutResponse)
async def get_active_workout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's currently active (not completed) workout"""
    
    workout = db.query(Workout).filter(
        Workout.user_id == current_user.id,
        Workout.is_completed == False
    ).order_by(Workout.started_at.desc()).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active workout found. Start a new one."
        )
    
    return WorkoutResponse.from_orm(workout)


@router.post("/{workout_id}/finish", response_model=WorkoutResponse)
async def finish_workout(
    workout_id: int,
    workout_finish: WorkoutFinish,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Finish a workout session"""
    
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    # Update metrics
    AnalyticsCalculator.update_workout_metrics(db, workout_id)
    db.refresh(workout)
    
    # Mark as completed
    workout.is_completed = True
    workout.finished_at = datetime.utcnow()
    workout.notes = workout_finish.notes
    workout.perceived_exertion = workout_finish.perceived_exertion
    
    # Calculate duration
    if workout.started_at and workout.finished_at:
        duration = (workout.finished_at - workout.started_at).total_seconds() / 60
        workout.duration_minutes = int(duration)
    
    db.commit()
    db.refresh(workout)
    
    return WorkoutResponse.from_orm(workout)


@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get workout details"""
    
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    return WorkoutResponse.from_orm(workout)


@router.get("/history/all", response_model=list[WorkoutResponse])
async def get_workout_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's workout history"""
    
    workouts = db.query(Workout).filter(
        Workout.user_id == current_user.id,
        Workout.is_completed == True
    ).order_by(
        Workout.started_at.desc()
    ).limit(limit).offset(offset).all()
    
    return [WorkoutResponse.from_orm(w) for w in workouts]


# ============================================================================
# WORKOUT EXERCISE ENDPOINTS
# ============================================================================

@router.post("/{workout_id}/exercises", response_model=WorkoutExerciseResponse)
async def add_exercise_to_workout(
    workout_id: int,
    exercise_data: WorkoutExerciseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an exercise to a workout"""
    
    # Verify workout exists and belongs to user
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    # Verify exercise exists
    exercise = db.query(Exercise).filter(
        Exercise.id == exercise_data.exercise_id
    ).first()
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    
    workout_exercise = WorkoutExercise(
        workout_id=workout_id,
        exercise_id=exercise_data.exercise_id,
        order=exercise_data.order,
        rpe=exercise_data.rpe,
        notes=exercise_data.notes
    )
    
    db.add(workout_exercise)
    db.commit()
    db.refresh(workout_exercise)
    
    return WorkoutExerciseResponse.from_orm(workout_exercise)


@router.put("/exercises/{workout_exercise_id}", response_model=WorkoutExerciseResponse)
async def update_workout_exercise(
    workout_exercise_id: int,
    exercise_data: WorkoutExerciseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update exercise in a workout"""
    
    workout_exercise = db.query(WorkoutExercise).filter(
        WorkoutExercise.id == workout_exercise_id
    ).first()
    
    if not workout_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout exercise not found"
        )
    
    # Verify access
    workout = db.query(Workout).filter(
        Workout.id == workout_exercise.workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this exercise"
        )
    
    # Update fields
    if exercise_data.order is not None:
        workout_exercise.order = exercise_data.order
    if exercise_data.rpe is not None:
        workout_exercise.rpe = exercise_data.rpe
    if exercise_data.notes is not None:
        workout_exercise.notes = exercise_data.notes
    
    db.commit()
    db.refresh(workout_exercise)
    
    return WorkoutExerciseResponse.from_orm(workout_exercise)


@router.delete("/exercises/{workout_exercise_id}")
async def delete_workout_exercise(
    workout_exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove an exercise from a workout"""
    
    workout_exercise = db.query(WorkoutExercise).filter(
        WorkoutExercise.id == workout_exercise_id
    ).first()
    
    if not workout_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout exercise not found"
        )
    
    # Verify access
    workout = db.query(Workout).filter(
        Workout.id == workout_exercise.workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    db.delete(workout_exercise)
    db.commit()
    
    return {"message": "Exercise removed from workout"}


# ============================================================================
# SET ENDPOINTS
# ============================================================================

@router.post("/exercises/{workout_exercise_id}/sets", response_model=SetResponse)
async def add_set(
    workout_exercise_id: int,
    set_data: SetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a set to an exercise"""
    
    # Verify workout exercise exists and user has access
    workout_exercise = db.query(WorkoutExercise).filter(
        WorkoutExercise.id == workout_exercise_id
    ).first()
    
    if not workout_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout exercise not found"
        )
    
    workout = db.query(Workout).filter(
        Workout.id == workout_exercise.workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Create set
    set_obj = Set(
        workout_exercise_id=workout_exercise_id,
        set_number=set_data.set_number,
        reps=set_data.reps,
        weight_kg=set_data.weight_kg,
        duration_seconds=set_data.duration_seconds,
        rpe=set_data.rpe,
        rir=set_data.rir,
        rest_seconds=set_data.rest_seconds,
        is_warmup=set_data.is_warmup,
        notes=set_data.notes,
        is_completed=True,
        completed_at=datetime.utcnow()
    )
    
    # Calculate metrics
    metrics = AnalyticsCalculator.calculate_set_metrics(set_obj)
    set_obj.volume_kg = metrics["volume_kg"]
    set_obj.estimated_1rm = metrics["estimated_1rm"]
    
    db.add(set_obj)
    db.commit()
    db.refresh(set_obj)
    
    # Check for new PRs
    prs = AnalyticsCalculator.detect_new_pr(db, set_obj, current_user.id)
    
    response = SetResponse.from_orm(set_obj)
    if prs:
        response.pr_achieved = prs
    
    return response


@router.put("/sets/{set_id}", response_model=SetResponse)
async def update_set(
    set_id: int,
    set_data: SetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a set"""
    
    set_obj = db.query(Set).filter(Set.id == set_id).first()
    
    if not set_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Set not found"
        )
    
    # Verify access
    workout_exercise = db.query(WorkoutExercise).filter(
        WorkoutExercise.id == set_obj.workout_exercise_id
    ).first()
    
    workout = db.query(Workout).filter(
        Workout.id == workout_exercise.workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Update fields
    if set_data.reps is not None:
        set_obj.reps = set_data.reps
    if set_data.weight_kg is not None:
        set_obj.weight_kg = set_data.weight_kg
    if set_data.duration_seconds is not None:
        set_obj.duration_seconds = set_data.duration_seconds
    if set_data.rpe is not None:
        set_obj.rpe = set_data.rpe
    if set_data.rir is not None:
        set_obj.rir = set_data.rir
    if set_data.rest_seconds is not None:
        set_obj.rest_seconds = set_data.rest_seconds
    if set_data.is_completed is not None:
        set_obj.is_completed = set_data.is_completed
        if set_data.is_completed:
            set_obj.completed_at = datetime.utcnow()
    if set_data.notes is not None:
        set_obj.notes = set_data.notes
    
    # Recalculate metrics
    metrics = AnalyticsCalculator.calculate_set_metrics(set_obj)
    set_obj.volume_kg = metrics["volume_kg"]
    set_obj.estimated_1rm = metrics["estimated_1rm"]
    
    db.commit()
    db.refresh(set_obj)
    
    return SetResponse.from_orm(set_obj)


@router.delete("/sets/{set_id}")
async def delete_set(
    set_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a set"""
    
    set_obj = db.query(Set).filter(Set.id == set_id).first()
    
    if not set_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Set not found"
        )
    
    # Verify access
    workout_exercise = db.query(WorkoutExercise).filter(
        WorkoutExercise.id == set_obj.workout_exercise_id
    ).first()
    
    workout = db.query(Workout).filter(
        Workout.id == workout_exercise.workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    db.delete(set_obj)
    db.commit()
    
    return {"message": "Set deleted successfully"}


@router.get("/sets/{set_id}", response_model=SetResponse)
async def get_set(
    set_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get set details"""
    
    set_obj = db.query(Set).filter(Set.id == set_id).first()
    
    if not set_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Set not found"
        )
    
    # Verify access
    workout_exercise = db.query(WorkoutExercise).filter(
        WorkoutExercise.id == set_obj.workout_exercise_id
    ).first()
    
    workout = db.query(Workout).filter(
        Workout.id == workout_exercise.workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    return SetResponse.from_orm(set_obj)
