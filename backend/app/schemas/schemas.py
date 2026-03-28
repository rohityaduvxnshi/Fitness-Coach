from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime


# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


# Profile Schemas
class ProfileCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    age: int = Field(..., ge=13, le=120)
    sex: str = Field(..., pattern="^(male|female)$")
    height_cm: float = Field(..., gt=0)
    weight_kg: float = Field(..., gt=0)
    body_fat_percentage: Optional[float] = Field(None, ge=1, le=99)


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    body_fat_percentage: Optional[float] = None


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    name: str
    age: int
    sex: str
    height_cm: float
    weight_kg: float
    body_fat_percentage: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Goal Schemas
class GoalCreate(BaseModel):
    goal_type: str = Field(..., pattern="^(weight_loss|weight_gain|recomposition)$")
    activity_level: str = Field(..., pattern="^(sedentary|light|moderate|very_active|extreme)$")
    target_weight_kg: Optional[float] = None


class GoalResponse(BaseModel):
    id: int
    user_id: int
    goal_type: str
    activity_level: str
    bmr: Optional[float]
    tdee: Optional[float]
    calorie_target: float
    protein_target_g: float
    carbs_target_g: float
    fat_target_g: float
    target_weight_kg: Optional[float]
    weeks_to_goal: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkoutPlanResponse(BaseModel):
    id: int
    goal_id: int
    plan_data: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GoalResponseWithPlan(GoalResponse):
    workout_plan: Optional[WorkoutPlanResponse] = None


# Progress Schemas
class ProgressLogCreate(BaseModel):
    weight_kg: float = Field(..., gt=0)
    body_fat_percentage: Optional[float] = Field(None, ge=1, le=99)
    notes: Optional[str] = Field(None, max_length=500)


class ProgressLogResponse(BaseModel):
    id: int
    user_id: int
    weight_kg: float
    body_fat_percentage: Optional[float]
    notes: Optional[str]
    logged_at: datetime
    
    class Config:
        from_attributes = True


# Dashboard Schemas
class DashboardResponse(BaseModel):
    user: UserResponse
    profile: ProfileResponse
    current_goal: Optional[GoalResponseWithPlan]
    recent_progress: list[ProgressLogResponse] = []
    
    class Config:
        from_attributes = True


# ============================================================================
# NEW: EXERCISE & WORKOUT SCHEMAS
# ============================================================================

# Exercise Category Schemas
class ExerciseCategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


# Muscle Group Schemas
class MuscleGroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


# Exercise Schemas
class ExerciseCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    category_id: Optional[int] = None
    primary_muscle_id: Optional[int] = None
    secondary_muscle_id: Optional[int] = None
    equipment: Optional[str] = None
    difficulty: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    movement_pattern: Optional[str] = Field(None, pattern="^(compound|isolation|dynamic_stretch|static_stretch)$")
    force_type: Optional[str] = Field(None, pattern="^(push|pull|legs|cardio|mobility)$")


class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    category_id: Optional[int] = None
    primary_muscle_id: Optional[int] = None
    secondary_muscle_id: Optional[int] = None
    equipment: Optional[str] = None
    difficulty: Optional[str] = None
    movement_pattern: Optional[str] = None
    force_type: Optional[str] = None
    is_active: Optional[bool] = None


class ExerciseResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    instructions: Optional[str]
    category_id: Optional[int]
    primary_muscle_id: Optional[int]
    secondary_muscle_id: Optional[int]
    equipment: Optional[str]
    difficulty: Optional[str]
    movement_pattern: Optional[str]
    force_type: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Set Schemas
class SetCreate(BaseModel):
    set_number: int = Field(..., ge=1)
    reps: Optional[int] = Field(None, ge=1)
    weight_kg: Optional[float] = Field(None, gt=0)
    duration_seconds: Optional[int] = Field(None, gt=0)
    rpe: Optional[float] = Field(None, ge=1, le=10)
    rir: Optional[int] = Field(None, ge=0)
    rest_seconds: Optional[int] = Field(None, ge=0)
    is_warmup: bool = False
    notes: Optional[str] = None


class SetUpdate(BaseModel):
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    duration_seconds: Optional[int] = None
    rpe: Optional[float] = None
    rir: Optional[int] = None
    rest_seconds: Optional[int] = None
    is_completed: Optional[bool] = None
    notes: Optional[str] = None


class SetResponse(BaseModel):
    id: int
    workout_exercise_id: int
    set_number: int
    is_warmup: bool
    reps: Optional[int]
    weight_kg: Optional[float]
    duration_seconds: Optional[int]
    rpe: Optional[float]
    rir: Optional[int]
    rest_seconds: Optional[int]
    completed_at: Optional[datetime]
    is_completed: bool
    notes: Optional[str]
    volume_kg: Optional[float]
    estimated_1rm: Optional[float]
    
    class Config:
        from_attributes = True


# Workout Exercise Schemas
class WorkoutExerciseCreate(BaseModel):
    exercise_id: int
    order: int = Field(..., ge=1)
    rpe: Optional[float] = Field(None, ge=1, le=10)
    notes: Optional[str] = None


class WorkoutExerciseUpdate(BaseModel):
    order: Optional[int] = None
    rpe: Optional[float] = None
    notes: Optional[str] = None


class WorkoutExerciseResponse(BaseModel):
    id: int
    workout_id: int
    exercise_id: int
    order: int
    total_sets: Optional[int]
    total_reps: Optional[int]
    total_volume_kg: Optional[float]
    notes: Optional[str]
    rpe: Optional[float]
    rest_seconds_avg: Optional[int]
    duration_minutes: Optional[int]
    sets: List[SetResponse] = []
    
    class Config:
        from_attributes = True


# Workout Schemas
class WorkoutStart(BaseModel):
    goal_id: Optional[int] = None
    name: Optional[str] = None
    notes: Optional[str] = None


class WorkoutFinish(BaseModel):
    notes: Optional[str] = None
    perceived_exertion: Optional[int] = Field(None, ge=1, le=10)


class WorkoutResponse(BaseModel):
    id: int
    user_id: int
    goal_id: Optional[int]
    name: Optional[str]
    started_at: datetime
    finished_at: Optional[datetime]
    is_completed: bool
    total_volume_kg: Optional[float]
    total_sets: Optional[int]
    total_reps: Optional[int]
    duration_minutes: Optional[int]
    notes: Optional[str]
    perceived_exertion: Optional[int]
    exercises: List[WorkoutExerciseResponse] = []
    
    class Config:
        from_attributes = True


# Exercise PR Schemas
class ExercisePRResponse(BaseModel):
    id: int
    user_id: int
    exercise_id: int
    heaviest_weight_kg: Optional[float]
    heaviest_weight_date: Optional[datetime]
    best_reps: Optional[int]
    best_reps_date: Optional[datetime]
    best_volume_kg: Optional[float]
    best_volume_date: Optional[datetime]
    best_estimated_1rm: Optional[float]
    best_1rm_date: Optional[datetime]
    first_logged_date: datetime
    last_logged_date: datetime
    total_sessions: int
    
    class Config:
        from_attributes = True


# Analytics Schemas
class ExerciseAnalyticsResponse(BaseModel):
    exercise_id: int
    exercise_name: str
    total_sessions: int
    heaviest_weight_kg: Optional[float]
    best_estimated_1rm: Optional[float]
    best_reps: Optional[int]
    best_volume_kg: Optional[float]
    recent_volume_kg: Optional[float]
    trend: str  # "increasing", "stable", "decreasing"
    last_session_date: Optional[datetime]


class WorkoutHistoryResponse(BaseModel):
    id: int
    name: Optional[str]
    started_at: datetime
    finished_at: Optional[datetime]
    duration_minutes: Optional[int]
    total_volume_kg: Optional[float]
    total_sets: Optional[int]
    total_reps: Optional[int]
    exercise_count: int
    perceived_exertion: Optional[int]


class AnalyticsSummaryResponse(BaseModel):
    total_workouts: int
    total_volume_all_time: float
    average_workout_volume: float
    weekly_frequency: float
    current_streak: int
    personal_records: List[ExercisePRResponse] = []
    recent_workouts: List[WorkoutHistoryResponse] = []


# ============================================================================
# WORKOUT PLAN GENERATION SCHEMAS
# ============================================================================

class WorkoutPlanGenerationRequest(BaseModel):
    """Request for generating a personalized workout plan"""
    goal: str = Field(..., pattern="^(cut|bulk|maintain)$")
    experience: str = Field(..., pattern="^(beginner|intermediate)$")
    days_per_week: int = Field(..., ge=3, le=6)
    equipment: str = Field(..., pattern="^(gym|home)$")
    focus: str = Field(..., pattern="^(strength|hypertrophy)$")


class WorkoutDayPlan(BaseModel):
    """Single day in workout plan"""
    day: int
    name: str
    muscle_groups: List[str]
    exercises: List[Dict]
    
    class Config:
        from_attributes = True


class WorkoutPlanGenerationResponse(BaseModel):
    """Response with complete personalized workout plan"""
    goal: str
    experience: str
    days_per_week: int
    equipment: str
    focus: str
    split_name: str
    duration_weeks: int
    days: List[WorkoutDayPlan]
    recommendations: Dict
    
    class Config:
        from_attributes = True
