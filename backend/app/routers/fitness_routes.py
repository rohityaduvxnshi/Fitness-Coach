import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.models import User, Profile, Goal, WorkoutPlan
from app.schemas.schemas import (
    GoalCreate, GoalResponseWithPlan, WorkoutPlanGenerationRequest,
    WorkoutPlanGenerationResponse
)
from app.services.fitness_calculator import FitnessCalculator
from app.services.workout_generator import WorkoutGenerator
from app.routers.user_routes import get_current_user

router = APIRouter(prefix="/fitness", tags=["fitness"])


@router.post("/goals", response_model=GoalResponseWithPlan, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create fitness goal and calculate plan"""
    
    # Get user's profile
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete your profile first"
        )
    
    # Calculate fitness metrics
    try:
        plan_data = FitnessCalculator.calculate_full_plan(
            weight_kg=profile.weight_kg,
            height_cm=profile.height_cm,
            age=profile.age,
            sex=profile.sex,
            body_fat_percentage=profile.body_fat_percentage or 20.0,
            goal_type=goal_data.goal_type,
            activity_level=goal_data.activity_level,
            target_weight_kg=goal_data.target_weight_kg
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Create goal
    new_goal = Goal(
        user_id=current_user.id,
        goal_type=goal_data.goal_type,
        activity_level=goal_data.activity_level,
        bmr=plan_data["bmr"],
        tdee=plan_data["tdee"],
        calorie_target=plan_data["calorie_target"],
        protein_target_g=plan_data["protein_target_g"],
        carbs_target_g=plan_data["carbs_target_g"],
        fat_target_g=plan_data["fat_target_g"],
        target_weight_kg=plan_data["target_weight_kg"],
        weeks_to_goal=plan_data["weeks_to_goal"]
    )
    
    db.add(new_goal)
    db.flush()
    
    # Generate workout plan with sensible defaults
    try:
        workout_plan_json = WorkoutGenerator.generate_plan(
            goal_type=goal_data.goal_type,
            experience="intermediate",  # Default to intermediate
            days_per_week=4,  # Default to 4 days/week
            equipment="gym",  # Default to gym
            focus="hypertrophy"  # Default to hypertrophy
        )
    except Exception as e:
        # If plan generation fails, create a basic workout plan
        workout_plan_json = json.dumps({
            "error": str(e),
            "goal_type": goal_data.goal_type,
            "activity_level": goal_data.activity_level,
            "message": "Workout plan generation failed, but goal was created successfully"
        })
    
    workout_plan = WorkoutPlan(
        goal_id=new_goal.id,
        plan_data=workout_plan_json
    )
    
    db.add(workout_plan)
    db.commit()
    db.refresh(new_goal)
    
    return new_goal


@router.get("/goals/current", response_model=GoalResponseWithPlan)
async def get_current_goal(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current fitness goal"""
    
    goal = db.query(Goal).filter(Goal.user_id == current_user.id).order_by(Goal.created_at.desc()).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No fitness goal found"
        )
    
    return goal


@router.get("/goals/{goal_id}", response_model=GoalResponseWithPlan)
async def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific fitness goal by ID"""
    
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    return goal


@router.post("/recalculate", response_model=GoalResponseWithPlan)
async def recalculate_goal(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Recalculate fitness goal based on updated profile"""
    
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    goal = db.query(Goal).filter(Goal.user_id == current_user.id).order_by(Goal.created_at.desc()).first()
    
    if not profile or not goal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile or goal not found"
        )
    
    # Recalculate metrics
    try:
        plan_data = FitnessCalculator.calculate_full_plan(
            weight_kg=profile.weight_kg,
            height_cm=profile.height_cm,
            age=profile.age,
            sex=profile.sex,
            body_fat_percentage=profile.body_fat_percentage or 20.0,
            goal_type=goal.goal_type,
            activity_level=goal.activity_level,
            target_weight_kg=goal.target_weight_kg
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Update goal
    goal.bmr = plan_data["bmr"]
    goal.tdee = plan_data["tdee"]
    goal.calorie_target = plan_data["calorie_target"]
    goal.protein_target_g = plan_data["protein_target_g"]
    goal.carbs_target_g = plan_data["carbs_target_g"]
    goal.fat_target_g = plan_data["fat_target_g"]
    goal.weeks_to_goal = plan_data["weeks_to_goal"]
    
    db.commit()
    db.refresh(goal)
    
    return goal

# ============================================================================
# INTELLIGENT WORKOUT PLAN GENERATION
# ============================================================================

@router.post("/generate-plan", response_model=dict)
async def generate_workout_plan(
    plan_request: WorkoutPlanGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a personalized workout plan based on user preferences
    
    Parameters:
    - goal: cut | bulk | maintain
    - experience: beginner | intermediate
    - days_per_week: 3-6
    - equipment: gym | home
    - focus: strength | hypertrophy
    
    Returns complete workout plan as JSON
    """
    
    try:
        import json
        plan_json = WorkoutGenerator.generate_plan(
            goal_type=plan_request.goal,
            experience=plan_request.experience,
            days_per_week=plan_request.days_per_week,
            equipment=plan_request.equipment,
            focus=plan_request.focus
        )
        
        # Parse JSON and return as dict
        plan_data = json.loads(plan_json)
        
        return {
            "success": True,
            "plan": plan_data,
            "message": f"Generated {plan_data['split_name']} workout plan"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate plan: {str(e)}"
        )