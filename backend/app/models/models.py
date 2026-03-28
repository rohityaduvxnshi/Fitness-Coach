from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base


class User(Base):
    """User model for authentication and account management"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    progress_logs = relationship("ProgressLog", back_populates="user", cascade="all, delete-orphan")
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan", foreign_keys="Workout.user_id")
    exercise_prs = relationship("ExercisePR", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"


class Profile(Base):
    """User profile model for storing personal metrics"""
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    sex = Column(String(10), nullable=False)  # 'male' or 'female'
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    body_fat_percentage = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<Profile {self.name}>"


class Goal(Base):
    """User fitness goals model"""
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_type = Column(String(50), nullable=False)  # 'weight_loss', 'weight_gain', 'recomposition'
    activity_level = Column(String(50), nullable=False)  # 'sedentary', 'light', 'moderate', 'very_active', 'extreme'
    
    # Calculated values
    bmr = Column(Float, nullable=True)  # Basal Metabolic Rate
    tdee = Column(Float, nullable=True)  # Total Daily Energy Expenditure
    calorie_target = Column(Float, nullable=False)
    protein_target_g = Column(Float, nullable=False)
    carbs_target_g = Column(Float, nullable=False)
    fat_target_g = Column(Float, nullable=False)
    
    # Duration and timeline
    target_weight_kg = Column(Float, nullable=True)
    weeks_to_goal = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="goals")
    workout_plan = relationship("WorkoutPlan", back_populates="goal", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Goal {self.goal_type}>"


class WorkoutPlan(Base):
    """Generated workout plan for user"""
    __tablename__ = "workout_plans"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False, unique=True)
    plan_data = Column(String(4000), nullable=False)  # JSON string containing the full plan
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    goal = relationship("Goal", back_populates="workout_plan")
    
    def __repr__(self):
        return f"<WorkoutPlan {self.goal_id}>"


class ProgressLog(Base):
    """User progress tracking logs"""
    __tablename__ = "progress_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    weight_kg = Column(Float, nullable=False)
    body_fat_percentage = Column(Float, nullable=True)
    notes = Column(String(500), nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="progress_logs")
    
    def __repr__(self):
        return f"<ProgressLog {self.user_id} at {self.logged_at}>"


# ============================================================================
# NEW: TRAINING EXECUTION & SET-LEVEL LOGGING
# ============================================================================


class ExerciseCategory(Base):
    """Exercise category for organization"""
    __tablename__ = "exercise_categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    exercises = relationship("Exercise", back_populates="category")
    
    def __repr__(self):
        return f"<ExerciseCategory {self.name}>"


class MuscleGroup(Base):
    """Muscle group classification"""
    __tablename__ = "muscle_groups"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)  # chest, back, legs, shoulders, arms, core
    description = Column(Text, nullable=True)
    
    # Relationships
    primary_exercises = relationship("Exercise", foreign_keys="Exercise.primary_muscle_id", back_populates="primary_muscle")
    secondary_exercises = relationship("Exercise", foreign_keys="Exercise.secondary_muscle_id", back_populates="secondary_muscle")
    
    def __repr__(self):
        return f"<MuscleGroup {self.name}>"


class Exercise(Base):
    """Exercise library/catalog"""
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(255), nullable=False, unique=True)  # URL-safe identifier
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    
    # Classification
    category_id = Column(Integer, ForeignKey("exercise_categories.id"), nullable=True)
    primary_muscle_id = Column(Integer, ForeignKey("muscle_groups.id"), nullable=True)
    secondary_muscle_id = Column(Integer, ForeignKey("muscle_groups.id"), nullable=True)
    
    # Exercise characteristics
    equipment = Column(String(100), nullable=True)  # barbell, dumbbell, machine, cable, bodyweight, etc.
    difficulty = Column(String(20), nullable=True)  # beginner, intermediate, advanced
    movement_pattern = Column(String(50), nullable=True)  # compound, isolation, dynamic_stretch, static_stretch
    
    # Tracking
    force_type = Column(String(20), nullable=True)  # push, pull, legs, cardio, mobility
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("ExerciseCategory", back_populates="exercises")
    primary_muscle = relationship("MuscleGroup", foreign_keys=[primary_muscle_id], back_populates="primary_exercises")
    secondary_muscle = relationship("MuscleGroup", foreign_keys=[secondary_muscle_id], back_populates="secondary_exercises")
    
    def __repr__(self):
        return f"<Exercise {self.name}>"


class Workout(Base):
    """One training session / workout"""
    __tablename__ = "workouts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True)  # Optional: linked to goal
    
    # Session info
    name = Column(String(255), nullable=True)  # e.g., "Chest & Triceps"
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)
    
    # Session metrics
    total_volume_kg = Column(Float, nullable=True)  # Auto-calculated
    total_sets = Column(Integer, nullable=True)  # Auto-calculated
    total_reps = Column(Integer, nullable=True)  # Auto-calculated
    duration_minutes = Column(Integer, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    perceived_exertion = Column(Integer, nullable=True)  # 1-10 RPE
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    goal = relationship("Goal", foreign_keys=[goal_id])
    exercises = relationship("WorkoutExercise", back_populates="workout", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Workout {self.id} for {self.user_id}>"


class WorkoutExercise(Base):
    """One exercise within one workout session"""
    __tablename__ = "workout_exercises"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    
    # Position/order in workout
    order = Column(Integer, nullable=False)  # 1st, 2nd, 3rd exercise
    
    # Metrics
    total_sets = Column(Integer, nullable=True)  # Auto-calculated
    total_reps = Column(Integer, nullable=True)  # Auto-calculated
    total_volume_kg = Column(Float, nullable=True)  # Auto-calculated
    
    # Exercise-specific notes
    notes = Column(Text, nullable=True)
    rpe = Column(Float, nullable=True)  # Rate of Perceived Exertion (1-10)
    
    # Timing
    rest_seconds_avg = Column(Integer, nullable=True)  # Average rest between sets
    duration_minutes = Column(Integer, nullable=True)
    
    # Relationships
    workout = relationship("Workout", back_populates="exercises")
    exercise = relationship("Exercise")
    sets = relationship("Set", back_populates="workout_exercise", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WorkoutExercise {self.exercise_id} in {self.workout_id}>"


class Set(Base):
    """One set for one exercise"""
    __tablename__ = "sets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workout_exercise_id = Column(Integer, ForeignKey("workout_exercises.id"), nullable=False)
    
    # Set info
    set_number = Column(Integer, nullable=False)  # 1st, 2nd, 3rd set
    is_warmup = Column(Boolean, default=False)
    
    # Performance data
    reps = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Effort
    rpe = Column(Float, nullable=True)  # Rate of Perceived Exertion (1-10)
    rir = Column(Integer, nullable=True)  # Reps in Reserve
    
    # Rest
    rest_seconds = Column(Integer, nullable=True)  # Rest after this set
    
    # Status
    completed_at = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Computed
    volume_kg = Column(Float, nullable=True)  # weight × reps (calculated)
    estimated_1rm = Column(Float, nullable=True)  # Calculated: weight × (1 + reps/30)
    
    # Relationships
    workout_exercise = relationship("WorkoutExercise", back_populates="sets")
    
    def __repr__(self):
        return f"<Set {self.set_number} of {self.workout_exercise_id}>"


class ExercisePR(Base):
    """Personal Records for exercises"""
    __tablename__ = "exercise_prs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    
    # PR types
    heaviest_weight_kg = Column(Float, nullable=True)
    heaviest_weight_set_id = Column(Integer, ForeignKey("sets.id"), nullable=True)
    heaviest_weight_date = Column(DateTime, nullable=True)
    
    best_reps = Column(Integer, nullable=True)
    best_reps_set_id = Column(Integer, ForeignKey("sets.id"), nullable=True)
    best_reps_date = Column(DateTime, nullable=True)
    
    best_volume_kg = Column(Float, nullable=True)  # Heaviest total volume in one set
    best_volume_set_id = Column(Integer, ForeignKey("sets.id"), nullable=True)
    best_volume_date = Column(DateTime, nullable=True)
    
    best_estimated_1rm = Column(Float, nullable=True)
    best_1rm_set_id = Column(Integer, ForeignKey("sets.id"), nullable=True)
    best_1rm_date = Column(DateTime, nullable=True)
    
    # Tracking
    first_logged_date = Column(DateTime, default=datetime.utcnow)
    last_logged_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_sessions = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    exercise = relationship("Exercise", foreign_keys=[exercise_id])
    
    def __repr__(self):
        return f"<ExercisePR {self.exercise_id} for user {self.user_id}>"
