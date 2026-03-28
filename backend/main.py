from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.config.database import engine, Base
from app.models.models import (
    User, Profile, Goal, WorkoutPlan, ProgressLog,
    Exercise, ExerciseCategory, MuscleGroup, Workout, 
    WorkoutExercise, Set, ExercisePR
)
from app.routers import (
    auth_routes, user_routes, fitness_routes, progress_routes,
    workout_routes, exercises_routes
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Personalized fitness coaching platform with AI-driven calculations"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Include routers
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(fitness_routes.router)
app.include_router(progress_routes.router)
app.include_router(workout_routes.router)
app.include_router(exercises_routes.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "endpoints": {
            "auth": "/docs#/auth",
            "users": "/docs#/users",
            "fitness": "/docs#/fitness",
            "progress": "/docs#/progress"
        }
    }


# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
