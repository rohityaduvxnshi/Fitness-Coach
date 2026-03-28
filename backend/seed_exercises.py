"""
Seed script to populate the exercise library with common exercises.
Run this once to initialize the database with exercise data.
"""
from app.config.database import SessionLocal, engine, Base
from app.models.models import ExerciseCategory, MuscleGroup, Exercise


def seed_muscle_groups(db):
    """Seed muscle groups"""
    muscle_groups = [
        MuscleGroup(name="Chest", description="Pectoral muscles"),
        MuscleGroup(name="Back", description="Latissimus, rhomboids, traps"),
        MuscleGroup(name="Shoulders", description="Deltoids and rotator cuff"),
        MuscleGroup(name="Biceps", description="Arm flexors"),
        MuscleGroup(name="Triceps", description="Arm extensors"),
        MuscleGroup(name="Forearms", description="Wrist and forearm muscles"),
        MuscleGroup(name="Quads", description="Quadriceps"),
        MuscleGroup(name="Hamstrings", description="Back of thigh"),
        MuscleGroup(name="Glutes", description="Gluteal muscles"),
        MuscleGroup(name="Calves", description="Calf muscles"),
        MuscleGroup(name="Core", description="Abdominals and stabilizers"),
    ]
    
    for mg in muscle_groups:
        existing = db.query(MuscleGroup).filter_by(name=mg.name).first()
        if not existing:
            db.add(mg)
    
    db.commit()
    print("✓ Muscle groups seeded")


def seed_exercise_categories(db):
    """Seed exercise categories"""
    categories = [
        ExerciseCategory(name="Strength", description="Resistance training"),
        ExerciseCategory(name="Cardio", description="Cardiovascular exercise"),
        ExerciseCategory(name="Flexibility", description="Stretching and mobility"),
        ExerciseCategory(name="Movement", description="Functional movement patterns"),
    ]
    
    for cat in categories:
        existing = db.query(ExerciseCategory).filter_by(name=cat.name).first()
        if not existing:
            db.add(cat)
    
    db.commit()
    print("✓ Exercise categories seeded")


def seed_exercises(db):
    """Seed common exercises"""
    
    # Get muscle groups
    chest = db.query(MuscleGroup).filter_by(name="Chest").first()
    back = db.query(MuscleGroup).filter_by(name="Back").first()
    shoulders = db.query(MuscleGroup).filter_by(name="Shoulders").first()
    biceps = db.query(MuscleGroup).filter_by(name="Biceps").first()
    triceps = db.query(MuscleGroup).filter_by(name="Triceps").first()
    quads = db.query(MuscleGroup).filter_by(name="Quads").first()
    hamstrings = db.query(MuscleGroup).filter_by(name="Hamstrings").first()
    glutes = db.query(MuscleGroup).filter_by(name="Glutes").first()
    core = db.query(MuscleGroup).filter_by(name="Core").first()
    
    # Get categories
    strength = db.query(ExerciseCategory).filter_by(name="Strength").first()
    
    exercises = [
        # Chest Exercises
        Exercise(
            name="Barbell Bench Press",
            slug="barbell-bench-press",
            category_id=strength.id,
            primary_muscle_id=chest.id,
            secondary_muscle_id=triceps.id,
            equipment="Barbell",
            difficulty="Intermediate",
            movement_pattern="Compound",
            force_type="Push"
        ),
        Exercise(
            name="Dumbbell Bench Press",
            slug="dumbbell-bench-press",
            category_id=strength.id,
            primary_muscle_id=chest.id,
            secondary_muscle_id=triceps.id,
            equipment="Dumbbell",
            difficulty="Intermediate",
            movement_pattern="Compound",
            force_type="Push"
        ),
        Exercise(
            name="Incline Bench Press",
            slug="incline-bench-press",
            category_id=strength.id,
            primary_muscle_id=chest.id,
            secondary_muscle_id=shoulders.id,
            equipment="Barbell",
            difficulty="Intermediate",
            movement_pattern="Compound",
            force_type="Push"
        ),
        Exercise(
            name="Cable Chest Fly",
            slug="cable-chest-fly",
            category_id=strength.id,
            primary_muscle_id=chest.id,
            equipment="Cable",
            difficulty="Beginner",
            movement_pattern="Isolation",
            force_type="Push"
        ),
        
        # Back Exercises
        Exercise(
            name="Barbell Deadlift",
            slug="barbell-deadlift",
            category_id=strength.id,
            primary_muscle_id=hamstrings.id,
            secondary_muscle_id=back.id,
            equipment="Barbell",
            difficulty="Intermediate",
            movement_pattern="Compound",
            force_type="Pull"
        ),
        Exercise(
            name="Barbell Row",
            slug="barbell-row",
            category_id=strength.id,
            primary_muscle_id=back.id,
            secondary_muscle_id=biceps.id,
            equipment="Barbell",
            difficulty="Intermediate",
            movement_pattern="Compound",
            force_type="Pull"
        ),
        Exercise(
            name="Lat Pulldown",
            slug="lat-pulldown",
            category_id=strength.id,
            primary_muscle_id=back.id,
            secondary_muscle_id=biceps.id,
            equipment="Machine",
            difficulty="Beginner",
            movement_pattern="Compound",
            force_type="Pull"
        ),
        Exercise(
            name="Dumbbell Row",
            slug="dumbbell-row",
            category_id=strength.id,
            primary_muscle_id=back.id,
            secondary_muscle_id=biceps.id,
            equipment="Dumbbell",
            difficulty="Intermediate",
            movement_pattern="Compound",
            force_type="Pull"
        ),
        
        # Leg Exercises
        Exercise(
            name="Barbell Squat",
            slug="barbell-squat",
            category_id=strength.id,
            primary_muscle_id=quads.id,
            secondary_muscle_id=glutes.id,
            equipment="Barbell",
            difficulty="Intermediate",
            movement_pattern="Compound",
            force_type="Legs"
        ),
        Exercise(
            name="Leg Press",
            slug="leg-press",
            category_id=strength.id,
            primary_muscle_id=quads.id,
            secondary_muscle_id=glutes.id,
            equipment="Machine",
            difficulty="Beginner",
            movement_pattern="Compound",
            force_type="Legs"
        ),
        Exercise(
            name="Romanian Deadlift",
            slug="romanian-deadlift",
            category_id=strength.id,
            primary_muscle_id=hamstrings.id,
            secondary_muscle_id=glutes.id,
            equipment="Barbell",
            difficulty="Intermediate",
            movement_pattern="Compound",
            force_type="Legs"
        ),
        Exercise(
            name="Leg Curl",
            slug="leg-curl",
            category_id=strength.id,
            primary_muscle_id=hamstrings.id,
            equipment="Machine",
            difficulty="Beginner",
            movement_pattern="Isolation",
            force_type="Legs"
        ),
        
        # Shoulder Exercises
        Exercise(
            name="Overhead Press",
            slug="overhead-press",
            category_id=strength.id,
            primary_muscle_id=shoulders.id,
            secondary_muscle_id=triceps.id,
            equipment="Barbell",
            difficulty="Intermediate",
            movement_pattern="Compound",
            force_type="Push"
        ),
        Exercise(
            name="Lateral Raise",
            slug="lateral-raise",
            category_id=strength.id,
            primary_muscle_id=shoulders.id,
            equipment="Dumbbell",
            difficulty="Beginner",
            movement_pattern="Isolation",
            force_type="Push"
        ),
        
        # Arm Exercises
        Exercise(
            name="Barbell Curl",
            slug="barbell-curl",
            category_id=strength.id,
            primary_muscle_id=biceps.id,
            equipment="Barbell",
            difficulty="Beginner",
            movement_pattern="Isolation",
            force_type="Pull"
        ),
        Exercise(
            name="Dumbbell Curl",
            slug="dumbbell-curl",
            category_id=strength.id,
            primary_muscle_id=biceps.id,
            equipment="Dumbbell",
            difficulty="Beginner",
            movement_pattern="Isolation",
            force_type="Pull"
        ),
        Exercise(
            name="Tricep Dips",
            slug="tricep-dips",
            category_id=strength.id,
            primary_muscle_id=triceps.id,
            equipment="Bodyweight",
            difficulty="Intermediate",
            movement_pattern="Compound",
            force_type="Push"
        ),
        Exercise(
            name="Rope Pushdown",
            slug="rope-pushdown",
            category_id=strength.id,
            primary_muscle_id=triceps.id,
            equipment="Cable",
            difficulty="Beginner",
            movement_pattern="Isolation",
            force_type="Push"
        ),
        
        # Core Exercises
        Exercise(
            name="Plank",
            slug="plank",
            category_id=strength.id,
            primary_muscle_id=core.id,
            equipment="Bodyweight",
            difficulty="Beginner",
            movement_pattern="Static",
            force_type="Core"
        ),
        Exercise(
            name="Crunch",
            slug="crunch",
            category_id=strength.id,
            primary_muscle_id=core.id,
            equipment="Bodyweight",
            difficulty="Beginner",
            movement_pattern="Isolation",
            force_type="Core"
        ),
    ]
    
    for exercise in exercises:
        existing = db.query(Exercise).filter_by(slug=exercise.slug).first()
        if not existing:
            db.add(exercise)
    
    db.commit()
    print(f"✓ {len(exercises)} exercises seeded")


def seed_database():
    """Run all seed functions"""
    
    # Create all tables first
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created\n")
    
    db = SessionLocal()
    
    try:
        print("📚 Seeding exercise library...\n")
        seed_muscle_groups(db)
        seed_exercise_categories(db)
        seed_exercises(db)
        print("\n✅ Database seeded successfully!\n")
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}\n")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
