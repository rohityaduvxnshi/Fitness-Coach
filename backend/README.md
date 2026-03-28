# FitCoach AI Backend

FastAPI-based backend for the FitCoach AI fitness coaching application.

## Setup

### 1. Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your values
```

### 4. Database Setup
```bash
mysql -u root -p
CREATE DATABASE fitnesscoach;
```

### 5. Run Server
```bash
uvicorn main:app --reload
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI.

## Project Structure

- `main.py` - FastAPI application entry point
- `app/config/` - Configuration and database setup
- `app/models/` - SQLAlchemy ORM models
- `app/schemas/` - Pydantic request/response schemas
- `app/routers/` - API route handlers
- `app/services/` - Business logic (calculations, generation)
- `app/utils/` - Utilities (JWT, password hashing)

## Key Services

### FitnessCalculator
Implements all fitness calculations:
- BMR (Basal Metabolic Rate)
- TDEE (Total Daily Energy Expenditure)
- Macro nutrient targets
- Progress timeline estimation

### WorkoutGenerator
Generates customized workout plans based on:
- Fitness goal (weight loss, gain, recomposition)
- Activity level
- 7-day workout split with exercises

## Database

Uses SQLAlchemy ORM with MySQL backend. Tables:
- users
- profiles
- goals
- workout_plans
- progress_logs

Schema is created automatically on first run.

## Authentication

JWT-based authentication with bcrypt password hashing.
- 24-hour token expiration
- Token refresh endpoints available

## Testing

Manual testing with curl:
```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "pass123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "pass123"}'
```

## Production Deployment

Use Gunicorn with Uvicorn workers:
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```
