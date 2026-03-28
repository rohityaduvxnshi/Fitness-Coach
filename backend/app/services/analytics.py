"""
Analytics and performance calculations for training data
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import (
    Set, WorkoutExercise, Workout, Exercise, ExercisePR, User
)


class AnalyticsCalculator:
    """Calculate fitness metrics and analytics"""
    
    @staticmethod
    def calculate_volume(weight_kg: float, reps: int) -> float:
        """Calculate volume for a set: weight × reps"""
        if not weight_kg or not reps:
            return 0
        return weight_kg * reps
    
    @staticmethod
    def calculate_estimated_1rm(weight_kg: float, reps: int) -> float:
        """
        Estimate 1RM using Brzycki formula:
        1RM = weight × (36 / (37 - reps))
        
        For low reps, also use:
        1RM = weight × (1 + reps / 30)  - Simpler approximation
        """
        if not weight_kg or reps <= 0:
            return 0
        
        if reps == 1:
            return weight_kg
        
        # Use Brzycki for 1-10 reps (more accurate)
        if reps <= 10:
            try:
                return weight_kg * (36 / (37 - reps))
            except ZeroDivisionError:
                return weight_kg
        
        # Use Epley for high reps (>10)
        return weight_kg * (1 + reps / 30)
    
    @staticmethod
    def calculate_set_metrics(set_obj: Set) -> dict:
        """Calculate all metrics for a set"""
        if not set_obj.weight_kg or not set_obj.reps:
            return {
                "volume_kg": 0,
                "estimated_1rm": 0
            }
        
        volume = AnalyticsCalculator.calculate_volume(set_obj.weight_kg, set_obj.reps)
        estimated_1rm = AnalyticsCalculator.calculate_estimated_1rm(set_obj.weight_kg, set_obj.reps)
        
        return {
            "volume_kg": volume,
            "estimated_1rm": estimated_1rm
        }
    
    @staticmethod
    def get_exercise_prs(db: Session, user_id: int, exercise_id: int) -> dict:
        """Get all PR data for a user's exercise"""
        
        # Get all completed sets for this exercise
        sets = db.query(Set).join(
            WorkoutExercise, Set.workout_exercise_id == WorkoutExercise.id
        ).join(
            Workout, WorkoutExercise.workout_id == Workout.id
        ).filter(
            Workout.user_id == user_id,
            WorkoutExercise.exercise_id == exercise_id,
            Set.is_completed == True
        ).order_by(Set.completed_at.desc()).all()
        
        if not sets:
            return {
                "heaviest_weight_kg": None,
                "heaviest_weight_date": None,
                "best_reps": None,
                "best_reps_date": None,
                "best_volume_kg": None,
                "best_volume_date": None,
                "best_estimated_1rm": None,
                "best_1rm_date": None,
                "total_sessions": 0
            }
        
        # Find PRs
        heaviest = max([s for s in sets if s.weight_kg], key=lambda s: s.weight_kg, default=None)
        best_reps_set = max([s for s in sets if s.reps], key=lambda s: s.reps, default=None)
        
        best_volume_set = None
        best_volume = 0
        for s in sets:
            if s.weight_kg and s.reps:
                volume = AnalyticsCalculator.calculate_volume(s.weight_kg, s.reps)
                if volume > best_volume:
                    best_volume = volume
                    best_volume_set = s
        
        best_1rm_set = None
        best_1rm = 0
        for s in sets:
            if s.weight_kg and s.reps:
                estimated_1rm = AnalyticsCalculator.calculate_estimated_1rm(s.weight_kg, s.reps)
                if estimated_1rm > best_1rm:
                    best_1rm = estimated_1rm
                    best_1rm_set = s
        
        # Count unique sessions
        unique_sessions = db.query(func.count(func.distinct(Workout.id))).join(
            WorkoutExercise, Workout.id == WorkoutExercise.workout_id
        ).join(
            Set, WorkoutExercise.id == Set.workout_exercise_id
        ).filter(
            Workout.user_id == user_id,
            WorkoutExercise.exercise_id == exercise_id,
            Set.is_completed == True
        ).scalar() or 0
        
        return {
            "heaviest_weight_kg": heaviest.weight_kg if heaviest else None,
            "heaviest_weight_date": heaviest.completed_at if heaviest else None,
            "best_reps": best_reps_set.reps if best_reps_set else None,
            "best_reps_date": best_reps_set.completed_at if best_reps_set else None,
            "best_volume_kg": best_volume if best_volume_set else None,
            "best_volume_date": best_volume_set.completed_at if best_volume_set else None,
            "best_estimated_1rm": best_1rm if best_1rm_set else None,
            "best_1rm_date": best_1rm_set.completed_at if best_1rm_set else None,
            "total_sessions": unique_sessions
        }
    
    @staticmethod
    def get_user_analytics(db: Session, user_id: int, days: int = 30) -> dict:
        """Get comprehensive analytics for a user"""
        
        # Get workouts in date range
        date_threshold = datetime.utcnow() - timedelta(days=days)
        workouts = db.query(Workout).filter(
            Workout.user_id == user_id,
            Workout.started_at >= date_threshold,
            Workout.is_completed == True
        ).all()
        
        # Calculate metrics
        total_workouts = len(workouts)
        total_volume = sum([w.total_volume_kg or 0 for w in workouts])
        average_volume = total_volume / total_workouts if total_workouts > 0 else 0
        
        # Weekly frequency
        unique_weeks = set()
        for w in workouts:
            week = w.started_at.isocalendar()[1]
            year = w.started_at.year
            unique_weeks.add((year, week))
        
        weeks_count = len(unique_weeks) if unique_weeks else 1
        weekly_frequency = total_workouts / weeks_count if weeks_count > 0 else 0
        
        # Current streak (consecutive days with workouts)
        if workouts:
            workouts_sorted = sorted(workouts, key=lambda w: w.started_at, reverse=True)
            current_streak = 1
            for i in range(len(workouts_sorted) - 1):
                days_diff = (workouts_sorted[i].started_at - 
                           workouts_sorted[i + 1].started_at).days
                if days_diff <= 1:
                    current_streak += 1
                else:
                    break
        else:
            current_streak = 0
        
        return {
            "total_workouts": total_workouts,
            "total_volume_all_time": total_volume,
            "average_workout_volume": average_volume,
            "weekly_frequency": weekly_frequency,
            "current_streak": current_streak,
            "time_period_days": days
        }
    
    @staticmethod
    def get_muscle_group_volume(db: Session, user_id: int, days: int = 7) -> dict:
        """Get volume per muscle group in time period"""
        from app.models.models import MuscleGroup
        
        date_threshold = datetime.utcnow() - timedelta(days=days)
        
        muscle_groups = db.query(MuscleGroup).all()
        volume_by_muscle = {}
        
        for mg in muscle_groups:
            # Count volume where exercise is primary muscle
            volume = db.query(func.sum(Set.weight_kg * Set.reps)).join(
                WorkoutExercise, Set.workout_exercise_id == WorkoutExercise.id
            ).join(
                Workout, WorkoutExercise.workout_id == Workout.id
            ).join(
                Exercise, WorkoutExercise.exercise_id == Exercise.id
            ).filter(
                Workout.user_id == user_id,
                Workout.started_at >= date_threshold,
                Workout.is_completed == True,
                Exercise.primary_muscle_id == mg.id
            ).scalar() or 0
            
            if volume > 0:
                volume_by_muscle[mg.name] = volume
        
        return volume_by_muscle
    
    @staticmethod
    def update_workout_metrics(db: Session, workout_id: int) -> None:
        """Auto-calculate and update workout totals"""
        workout = db.query(Workout).filter(Workout.id == workout_id).first()
        if not workout:
            return
        
        # Get all exercises in workout
        exercises = db.query(WorkoutExercise).filter(
            WorkoutExercise.workout_id == workout_id
        ).all()
        
        total_sets = 0
        total_reps = 0
        total_volume = 0
        
        for exercise in exercises:
            sets = db.query(Set).filter(
                Set.workout_exercise_id == exercise.id,
                Set.is_completed == True
            ).all()
            
            exercise_sets = len(sets)
            exercise_reps = sum([s.reps or 0 for s in sets])
            exercise_volume = sum([
                (s.weight_kg or 0) * (s.reps or 0) for s in sets
            ])
            
            exercise.total_sets = exercise_sets
            exercise.total_reps = exercise_reps
            exercise.total_volume_kg = exercise_volume
            
            total_sets += exercise_sets
            total_reps += exercise_reps
            total_volume += exercise_volume
        
        workout.total_sets = total_sets
        workout.total_reps = total_reps
        workout.total_volume_kg = total_volume
        
        db.commit()
    
    @staticmethod
    def detect_new_pr(db: Session, set_obj: Set, user_id: int) -> list:
        """Check if a set is a new PR and return PR types achieved"""
        if not set_obj.is_completed or not set_obj.weight_kg:
            return []
        
        workout_exercise = db.query(WorkoutExercise).filter(
            WorkoutExercise.id == set_obj.workout_exercise_id
        ).first()
        
        if not workout_exercise:
            return []
        
        exercise_id = workout_exercise.exercise_id
        prs_achieved = []
        
        # Get current PRs
        pr_data = AnalyticsCalculator.get_exercise_prs(db, user_id, exercise_id)
        
        # Check weight PR
        if not pr_data["heaviest_weight_kg"] or set_obj.weight_kg > pr_data["heaviest_weight_kg"]:
            prs_achieved.append("heaviest_weight")
        
        # Check reps PR
        if set_obj.reps and (not pr_data["best_reps"] or set_obj.reps > pr_data["best_reps"]):
            prs_achieved.append("best_reps")
        
        # Check volume PR
        if set_obj.weight_kg and set_obj.reps:
            current_volume = set_obj.weight_kg * set_obj.reps
            if not pr_data["best_volume_kg"] or current_volume > pr_data["best_volume_kg"]:
                prs_achieved.append("best_volume")
        
        # Check 1RM PR
        if set_obj.weight_kg and set_obj.reps:
            estimated_1rm = AnalyticsCalculator.calculate_estimated_1rm(
                set_obj.weight_kg, set_obj.reps
            )
            if not pr_data["best_estimated_1rm"] or estimated_1rm > pr_data["best_estimated_1rm"]:
                prs_achieved.append("best_1rm")
        
        return prs_achieved
