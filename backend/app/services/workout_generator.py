import json
import random
from typing import Dict, List, Optional


class WorkoutGenerator:
    """Service for generating intelligent, personalized workout plans"""
    
    # ============================================================================
    # EXERCISE POOLS by MUSCLE GROUP
    # ============================================================================
    
    EXERCISE_POOLS = {
        "chest": [
            {"name": "Barbell Bench Press", "type": "compound", "equipment": "barbell"},
            {"name": "Incline Barbell Bench Press", "type": "compound", "equipment": "barbell"},
            {"name": "Dumbbell Bench Press", "type": "compound", "equipment": "dumbbell"},
            {"name": "Incline Dumbbell Press", "type": "compound", "equipment": "dumbbell"},
            {"name": "Cable Chest Press", "type": "compound", "equipment": "cable"},
            {"name": "Machine Chest Press", "type": "compound", "equipment": "machine"},
            {"name": "Cable Flye", "type": "isolation", "equipment": "cable"},
            {"name": "Pec Deck Machine", "type": "isolation", "equipment": "machine"},
            {"name": "Dumbbell Flye", "type": "isolation", "equipment": "dumbbell"},
            {"name": "Push-ups", "type": "compound", "equipment": "bodyweight"},
        ],
        "back": [
            {"name": "Barbell Deadlift", "type": "compound", "equipment": "barbell"},
            {"name": "Barbell Bent-Over Row", "type": "compound", "equipment": "barbell"},
            {"name": "Dumbbell Row", "type": "compound", "equipment": "dumbbell"},
            {"name": "Machine Row", "type": "compound", "equipment": "machine"},
            {"name": "Cable Row", "type": "compound", "equipment": "cable"},
            {"name": "Lat Pulldown", "type": "compound", "equipment": "machine"},
            {"name": "Pull-ups", "type": "compound", "equipment": "bodyweight"},
            {"name": "Assisted Pull-ups", "type": "compound", "equipment": "machine"},
            {"name": "Face Pulls", "type": "isolation", "equipment": "cable"},
            {"name": "Reverse Pec Deck", "type": "isolation", "equipment": "machine"},
        ],
        "legs": [
            {"name": "Barbell Squat", "type": "compound", "equipment": "barbell"},
            {"name": "Leg Press", "type": "compound", "equipment": "machine"},
            {"name": "Goblet Squat", "type": "compound", "equipment": "dumbbell"},
            {"name": "Romanian Deadlift", "type": "compound", "equipment": "barbell"},
            {"name": "Hack Squat", "type": "compound", "equipment": "machine"},
            {"name": "Smith Machine Squat", "type": "compound", "equipment": "barbell"},
            {"name": "Leg Curl", "type": "isolation", "equipment": "machine"},
            {"name": "Leg Extension", "type": "isolation", "equipment": "machine"},
            {"name": "Leg Press", "type": "compound", "equipment": "machine"},
            {"name": "Calf Raise", "type": "isolation", "equipment": "machine"},
        ],
        "shoulders": [
            {"name": "Barbell Overhead Press", "type": "compound", "equipment": "barbell"},
            {"name": "Dumbbell Overhead Press", "type": "compound", "equipment": "dumbbell"},
            {"name": "Machine Shoulder Press", "type": "compound", "equipment": "machine"},
            {"name": "Lateral Raise", "type": "isolation", "equipment": "dumbbell"},
            {"name": "Cable Lateral Raise", "type": "isolation", "equipment": "cable"},
            {"name": "Machine Lateral Raise", "type": "isolation", "equipment": "machine"},
            {"name": "Reverse Flye", "type": "isolation", "equipment": "dumbbell"},
            {"name": "Reverse Pec Deck", "type": "isolation", "equipment": "machine"},
            {"name": "Upright Row", "type": "compound", "equipment": "barbell"},
            {"name": "Pike Push-ups", "type": "isolation", "equipment": "bodyweight"},
        ],
        "biceps": [
            {"name": "Barbell Curl", "type": "isolation", "equipment": "barbell"},
            {"name": "Dumbbell Curl", "type": "isolation", "equipment": "dumbbell"},
            {"name": "Cable Curl", "type": "isolation", "equipment": "cable"},
            {"name": "Machine Curl", "type": "isolation", "equipment": "machine"},
            {"name": "EZ-Bar Curl", "type": "isolation", "equipment": "barbell"},
            {"name": "Incline Dumbbell Curl", "type": "isolation", "equipment": "dumbbell"},
            {"name": "Preacher Curl", "type": "isolation", "equipment": "barbell"},
            {"name": "Concentration Curl", "type": "isolation", "equipment": "dumbbell"},
        ],
        "triceps": [
            {"name": "Tricep Dips", "type": "compound", "equipment": "bodyweight"},
            {"name": "Tricep Rope Pushdown", "type": "isolation", "equipment": "cable"},
            {"name": "Overhead Tricep Extension", "type": "isolation", "equipment": "cable"},
            {"name": "Skull Crushers", "type": "isolation", "equipment": "barbell"},
            {"name": "Dumbbell Overhead Extension", "type": "isolation", "equipment": "dumbbell"},
            {"name": "Machine Dip", "type": "compound", "equipment": "machine"},
            {"name": "Close-Grip Bench Press", "type": "compound", "equipment": "barbell"},
            {"name": "Tricep Kickback", "type": "isolation", "equipment": "dumbbell"},
        ],
    }
    
    # ============================================================================
    # SPLIT SELECTION LOGIC
    # ============================================================================
    
    SPLITS = {
        "full_body_3x": {
            "name": "Full Body (3x/week)",
            "days": [
                {"name": "Full Body A", "muscle_groups": ["chest", "back", "legs", "shoulders"]},
                {"name": "Full Body B", "muscle_groups": ["chest", "back", "legs", "shoulders"]},
                {"name": "Full Body C", "muscle_groups": ["chest", "back", "legs", "shoulders"]},
            ]
        },
        "upper_lower_4x": {
            "name": "Upper/Lower (4x/week)",
            "days": [
                {"name": "Upper A", "muscle_groups": ["chest", "back", "shoulders", "biceps"]},
                {"name": "Lower A", "muscle_groups": ["legs"]},
                {"name": "Upper B", "muscle_groups": ["chest", "back", "shoulders", "triceps"]},
                {"name": "Lower B", "muscle_groups": ["legs"]},
            ]
        },
        "upper_lower_5x": {
            "name": "Upper/Lower + Arms (5x/week)",
            "days": [
                {"name": "Upper A", "muscle_groups": ["chest", "back", "shoulders"]},
                {"name": "Lower A", "muscle_groups": ["legs"]},
                {"name": "Upper B", "muscle_groups": ["chest", "back", "shoulders"]},
                {"name": "Lower B", "muscle_groups": ["legs"]},
                {"name": "Arms", "muscle_groups": ["biceps", "triceps"]},
            ]
        },
        "ppl_6x": {
            "name": "Push/Pull/Legs (6x/week)",
            "days": [
                {"name": "Push A", "muscle_groups": ["chest", "shoulders", "triceps"]},
                {"name": "Pull A", "muscle_groups": ["back", "biceps"]},
                {"name": "Legs A", "muscle_groups": ["legs"]},
                {"name": "Push B", "muscle_groups": ["chest", "shoulders", "triceps"]},
                {"name": "Pull B", "muscle_groups": ["back", "biceps"]},
                {"name": "Legs B", "muscle_groups": ["legs"]},
            ]
        },
    }
    
    @staticmethod
    def generate_plan(
        goal_type: str,
        experience: str,
        days_per_week: int,
        equipment: str,
        focus: str
    ) -> str:
        """
        Generate a personalized workout plan
        
        Args:
            goal_type: "cut" | "bulk" | "maintain"
            experience: "beginner" | "intermediate"
            days_per_week: 3-6
            equipment: "gym" | "home"
            focus: "strength" | "hypertrophy"
        
        Returns: JSON string of the complete plan
        """
        
        # Step 1: Select appropriate split
        split = WorkoutGenerator._select_split(experience, days_per_week)
        
        # Step 2: Get split definition
        split_def = WorkoutGenerator.SPLITS.get(split)
        if not split_def:
            raise ValueError(f"Invalid split: {split}")
        
        # Step 3: Generate exercises for each day
        plan = {
            "goal": goal_type,
            "experience": experience,
            "days_per_week": days_per_week,
            "equipment": equipment,
            "focus": focus,
            "split_name": split_def["name"],
            "duration_weeks": 12,
            "days": []
        }
        
        for i, day_config in enumerate(split_def["days"], 1):
            day_plan = {
                "day": i,
                "name": day_config["name"],
                "muscle_groups": day_config["muscle_groups"],
                "exercises": []
            }
            
            # Select exercises for this day's muscle groups
            seen_exercises = set()
            for muscle_group in day_config["muscle_groups"]:
                exercises = WorkoutGenerator._select_exercises(
                    muscle_group,
                    2 if experience == "beginner" else 3,
                    equipment,
                    seen_exercises
                )
                
                for exercise in exercises:
                    seen_exercises.add(exercise["name"])
                    
                    sets, reps = WorkoutGenerator._assign_sets_reps(
                        focus,
                        experience,
                        exercise["type"]
                    )
                    
                    day_plan["exercises"].append({
                        "name": exercise["name"],
                        "muscle_group": muscle_group,
                        "type": exercise["type"],
                        "equipment": exercise["equipment"],
                        "sets": sets,
                        "reps": reps,
                        "rest_seconds": WorkoutGenerator._get_rest_seconds(reps)
                    })
            
            plan["days"].append(day_plan)
        
        # Add metadata and recommendations
        plan.update(WorkoutGenerator._add_plan_metadata(goal_type, experience, focus))
        
        return json.dumps(plan, indent=2)
    
    @staticmethod
    def _select_split(experience: str, days_per_week: int) -> str:
        """Select appropriate training split based on experience and frequency"""
        
        if experience == "beginner":
            if days_per_week == 3:
                return "full_body_3x"
            elif days_per_week == 4:
                return "upper_lower_4x"
            elif days_per_week in [5, 6]:
                return "upper_lower_5x"
        else:  # intermediate
            if days_per_week == 3:
                return "full_body_3x"
            elif days_per_week == 4:
                return "upper_lower_4x"
            elif days_per_week == 5:
                return "upper_lower_5x"
            elif days_per_week == 6:
                return "ppl_6x"
        
        # Default
        return "upper_lower_4x"
    
    @staticmethod
    def _select_exercises(
        muscle_group: str,
        count: int,
        equipment: str,
        exclude: set
    ) -> List[Dict]:
        """Select diverse exercises from pool, excluding already selected"""
        
        pool = WorkoutGenerator.EXERCISE_POOLS.get(muscle_group, [])
        
        # Filter by equipment if home user
        if equipment == "home":
            pool = [e for e in pool if e["equipment"] in ["dumbbell", "bodyweight"]]
        
        # Filter out already selected
        pool = [e for e in pool if e["name"] not in exclude]
        
        # Ensure mix of compound and isolation
        compounds = [e for e in pool if e["type"] == "compound"]
        isolations = [e for e in pool if e["type"] == "isolation"]
        
        selected = []
        
        # Always pick compounds first
        if compounds:
            selected.extend(random.sample(compounds, min(1, len(compounds))))
        
        # Fill remaining with random selection
        remaining = [e for e in pool if e not in selected]
        if remaining:
            needed = count - len(selected)
            selected.extend(random.sample(remaining, min(needed, len(remaining))))
        
        return selected[:count]
    
    @staticmethod
    def _assign_sets_reps(focus: str, experience: str, exercise_type: str) -> tuple:
        """Determine sets and rep range based on training focus"""
        
        rep_ranges = {
            "strength": "4-6",
            "hypertrophy": "8-12"
        }
        
        reps = rep_ranges.get(focus, "8-10")
        
        # Adjust sets based on experience and exercise type
        base_sets = 3 if experience == "beginner" else 4
        
        if exercise_type == "isolation":
            base_sets -= 1
        
        if focus == "strength":
            base_sets = max(3, base_sets)
        
        return base_sets, reps
    
    @staticmethod
    def _get_rest_seconds(reps: str) -> int:
        """Determine rest time based on rep range"""
        
        if reps.startswith("4"):  # 4-6 range
            return 180  # 3 min
        elif reps.startswith("8"):  # 8-12 range
            return 90   # 90 sec
        else:
            return 120  # 2 min default
    
    @staticmethod
    def _add_plan_metadata(goal_type: str, experience: str, focus: str) -> Dict:
        """Add recommended guidelines and metadata"""
        
        metadata = {"recommendations": {}}
        
        # Goal-specific notes
        if goal_type == "cut":
            metadata["recommendations"]["diet"] = "Calorie deficit (300-500 below TDEE), high protein"
            metadata["recommendations"]["cardio"] = "3-4 sessions, 30-45 min per week"
            metadata["recommendations"]["intensity"] = "High rep ranges, shorter rest periods"
        
        elif goal_type == "bulk":
            metadata["recommendations"]["diet"] = "Calorie surplus (300-500 above TDEE), high protein"
            metadata["recommendations"]["cardio"] = "1-2 light sessions, 20-30 min per week"
            metadata["recommendations"]["intensity"] = "Lower rep ranges, longer rest periods"
        
        else:  # maintain
            metadata["recommendations"]["diet"] = "Maintenance calories, moderate protein"
            metadata["recommendations"]["cardio"] = "2-3 sessions, 30 min per week"
            metadata["recommendations"]["intensity"] = "Moderate rep ranges, balanced intensity"
        
        metadata["recommendations"]["progression"] = "Increase weight by 2.5-5% when you hit top end of rep range"
        metadata["recommendations"]["deload"] = "Every 8-10 weeks, reduce volume by 40-50%"
        metadata["recommendations"]["duration"] = "Follow this plan for 12 weeks before adjusting"
        
        return metadata
