import math
from typing import Dict, Tuple


class FitnessCalculator:
    """Service for fitness calculations"""
    
    # Activity level multipliers
    ACTIVITY_MULTIPLIERS = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "very_active": 1.725,
        "extreme": 1.9
    }
    
    # Goal-specific calorie adjustments
    CALORIE_ADJUSTMENTS = {
        "weight_loss": (-500, -300),  # min, max deficit
        "weight_gain": (300, 500),    # min, max surplus
        "recomposition": (-200, -100)  # min, max deficit
    }
    
    @staticmethod
    def calculate_bmr(
        weight_kg: float,
        height_cm: float,
        age: int,
        sex: str
    ) -> float:
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor formula
        
        Men: BMR = (10 × weight_kg) + (6.25 × height_cm) − (5 × age) + 5
        Women: BMR = (10 × weight_kg) + (6.25 × height_cm) − (5 × age) − 161
        """
        if sex.lower() == "male":
            return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        elif sex.lower() == "female":
            return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        else:
            raise ValueError("Sex must be 'male' or 'female'")
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        """
        Calculate Total Daily Energy Expenditure
        TDEE = BMR × activity_multiplier
        """
        if activity_level not in FitnessCalculator.ACTIVITY_MULTIPLIERS:
            raise ValueError(f"Invalid activity level: {activity_level}")
        
        multiplier = FitnessCalculator.ACTIVITY_MULTIPLIERS[activity_level]
        return bmr * multiplier
    
    @staticmethod
    def calculate_lean_body_mass(weight_kg: float, body_fat_percentage: float) -> float:
        """
        Calculate Lean Body Mass
        LBM = weight × (1 − bodyFat%)
        """
        if body_fat_percentage < 0 or body_fat_percentage > 100:
            raise ValueError("Body fat percentage must be between 0 and 100")
        
        return weight_kg * (1 - (body_fat_percentage / 100))
    
    @staticmethod
    def calculate_adjusted_calories(
        tdee: float,
        goal_type: str
    ) -> float:
        """
        Calculate adjusted calorie target based on goal
        """
        if goal_type not in FitnessCalculator.CALORIE_ADJUSTMENTS:
            raise ValueError(f"Invalid goal type: {goal_type}")
        
        min_adj, max_adj = FitnessCalculator.CALORIE_ADJUSTMENTS[goal_type]
        
        if goal_type == "weight_loss":
            # Use middle of range for weight loss
            adjustment = (min_adj + max_adj) / 2
        elif goal_type == "weight_gain":
            # Use middle of range for weight gain
            adjustment = (min_adj + max_adj) / 2
        else:  # recomposition
            # Use middle of range for recomposition
            adjustment = (min_adj + max_adj) / 2
        
        return tdee + adjustment
    
    @staticmethod
    def calculate_macros(
        calorie_target: float,
        weight_kg: float,
        goal_type: str
    ) -> Dict[str, float]:
        """
        Calculate macro nutrient targets
        
        Protein: 1.6 – 2.2 g per kg (use 2.0 for simplicity)
        Fat: 20 – 30 % of calories (use 25%)
        Carbs: remaining calories
        """
        # Protein target: 2.0g per kg for all goals
        protein_g = weight_kg * 2.0
        protein_calories = protein_g * 4  # 4 kcal per gram
        
        # Fat target: 25% of total calories
        fat_calories = calorie_target * 0.25
        fat_g = fat_calories / 9  # 9 kcal per gram
        
        # Carbs: remaining calories
        carbs_calories = calorie_target - protein_calories - fat_calories
        carbs_g = carbs_calories / 4  # 4 kcal per gram
        
        # Ensure carbs don't go negative (adjust if needed)
        if carbs_g < 0:
            fat_g = (calorie_target - protein_calories) * 0.7 / 9
            carbs_g = (calorie_target - protein_calories - (fat_g * 9)) / 4
        
        return {
            "protein_g": round(protein_g, 1),
            "fat_g": round(fat_g, 1),
            "carbs_g": round(carbs_g, 1)
        }
    
    @staticmethod
    def estimate_timeline(
        current_weight_kg: float,
        target_weight_kg: float,
        goal_type: str
    ) -> int:
        """
        Estimate weeks to reach goal
        
        Typical rates:
        - Weight loss: 0.5-1.0 kg per week
        - Weight gain: 0.25-0.5 kg per week
        - Recomposition: 0.25 kg per week
        """
        weight_change = abs(target_weight_kg - current_weight_kg)
        
        if goal_type == "weight_loss":
            weekly_rate = 0.75  # kg per week
        elif goal_type == "weight_gain":
            weekly_rate = 0.4   # kg per week
        else:  # recomposition
            weekly_rate = 0.25  # kg per week
        
        weeks = weight_change / weekly_rate if weekly_rate > 0 else 1
        return max(1, round(weeks))
    
    @staticmethod
    def calculate_full_plan(
        weight_kg: float,
        height_cm: float,
        age: int,
        sex: str,
        body_fat_percentage: float,
        goal_type: str,
        activity_level: str,
        target_weight_kg: float = None
    ) -> Dict:
        """
        Calculate complete fitness plan including all metrics
        """
        # Basic calculations
        bmr = FitnessCalculator.calculate_bmr(weight_kg, height_cm, age, sex)
        tdee = FitnessCalculator.calculate_tdee(bmr, activity_level)
        calorie_target = FitnessCalculator.calculate_adjusted_calories(tdee, goal_type)
        macros = FitnessCalculator.calculate_macros(calorie_target, weight_kg, goal_type)
        
        # Timeline calculation
        if target_weight_kg is None:
            if goal_type == "weight_loss":
                target_weight_kg = weight_kg * 0.9  # 10% weight loss
            elif goal_type == "weight_gain":
                target_weight_kg = weight_kg * 1.1  # 10% weight gain
            else:  # recomposition
                target_weight_kg = weight_kg
        
        weeks_to_goal = FitnessCalculator.estimate_timeline(weight_kg, target_weight_kg, goal_type)
        
        return {
            "bmr": round(bmr, 1),
            "tdee": round(tdee, 1),
            "calorie_target": round(calorie_target, 1),
            "protein_target_g": macros["protein_g"],
            "fat_target_g": macros["fat_g"],
            "carbs_target_g": macros["carbs_g"],
            "target_weight_kg": round(target_weight_kg, 1),
            "weeks_to_goal": weeks_to_goal
        }
