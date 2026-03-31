# Copilot Prompt: alwaysdata deployment prep for Fitness-Coach

You are working inside the existing `Fitness-Coach` repository.

Goal: prepare this project for deployment on **alwaysdata** with this target architecture:
- Angular frontend deployed as **Static Files**
- FastAPI backend deployed as **User Program**
- MariaDB/MySQL hosted on alwaysdata
- No Docker, no Redis, no major architecture rewrite

## Current repo facts you must respect
- Backend entrypoint exists at `backend/main.py`
- Backend settings file exists at `backend/app/config/settings.py`
- Backend database config exists at `backend/app/config/database.py`
- Backend dependencies exist at `backend/requirements.txt`
- The backend currently imports `BaseSettings` from `pydantic_settings`
- The backend currently has a `/health` endpoint

## What you must do

### 1. Fix backend deployment readiness
- Update `backend/requirements.txt` to include **pydantic-settings** because it is imported in the code.
- Refactor `backend/app/config/settings.py` so production config is cleanly environment-driven.
- Add support for:
  - `DEBUG`
  - `SECRET_KEY`
  - `DATABASE_URL`
  - `CORS_ORIGINS`
  - `PORT`
- Parse `CORS_ORIGINS` from an environment string like:
  - `https://frontend.example.com`
  - or comma-separated values if multiple origins are provided
- Keep backward compatibility for local development.

### 2. Fix backend production defaults
- In `backend/app/config/database.py`:
  - stop forcing `echo=True` in production
  - use the central settings object instead of re-reading env manually where reasonable
  - keep sqlite support for local development if it already exists
  - keep MySQL support for production
  - keep `pool_pre_ping=True`
- In `backend/main.py`:
  - make the local `__main__` runner use the configurable `PORT`
  - keep `host="0.0.0.0"`
  - do not break the existing app import path `main:app`

### 3. Add deployment support files
Create these files if they do not already exist:
- `backend/.env.example`
- `backend/.env.production.example`
- `backend/alwaysdata_start.sh`
- `DEPLOY_ALWAYS_DATA.md`

Contents requirements:
- `.env.example` should be local-dev friendly
- `.env.production.example` should show alwaysdata-style placeholders for MySQL and frontend origin
- `alwaysdata_start.sh` should run the backend with a command equivalent to:
  - `python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}`
- `DEPLOY_ALWAYS_DATA.md` should explain:
  - how to create the alwaysdata database
  - how to upload files
  - how to configure a User Program backend site
  - how to configure a Static Files frontend site
  - how to test `/health`

### 4. Prepare frontend for production
Locate the Angular app in the repository and do all of the following:
- identify the production environment config file(s)
- replace localhost API assumptions with an environment-driven API base URL
- ensure production builds point to the deployed backend URL
- do not hardcode local-only URLs in production config
- keep local development behavior intact

### 5. Preserve behavior
- Do not change business logic, database models, or API routes unless required for deployment safety.
- Do not remove existing endpoints.
- Do not redesign the app.
- Make the smallest safe deployment-oriented changes.

## Output format
1. First, list every file you plan to modify.
2. Then apply the changes.
3. Then provide a short deployment checklist.
4. Then provide the exact alwaysdata backend launch command and the expected frontend build output directory.

## Code quality requirements
- No placeholders inside executable code except documented example env files.
- Production-safe defaults.
- Clear comments only where necessary.
- Do not introduce Docker.
- Do not introduce Redis.
- Do not switch away from FastAPI, Angular, or MySQL.
