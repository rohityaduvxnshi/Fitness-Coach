# Deploying Fitness-Coach on alwaysdata

This guide is tailored to the current repository layout and backend code.

## 1) What to prepare before deployment

### Backend
- Confirm the backend entrypoint remains `backend/main.py`.
- Confirm the production launch command can run the FastAPI app from the `backend/` directory.
- Make sure all Python dependencies required on a clean host are listed in `backend/requirements.txt`.
- Add `pydantic-settings` to requirements because `backend/app/config/settings.py` imports `BaseSettings` from `pydantic_settings`.
- Make production configuration fully environment-driven.
- Avoid hard-coded localhost-only CORS values in production.
- Do not leave SQLAlchemy `echo=True` in production.
- Make sure `DATABASE_URL` points to the alwaysdata MariaDB/MySQL host.
- Keep `/health` working for deployment verification.

### Frontend
- Build Angular in production mode.
- Identify the actual Angular build output directory and deploy that directory as an alwaysdata Static Files site.
- Replace localhost API URLs with an environment-driven production API base URL.
- Verify auth/login/register/workout/progress calls point to the production backend domain.

### Environment variables to define
- `DEBUG=False`
- `SECRET_KEY=<strong-random-secret>`
- `DATABASE_URL=mysql+pymysql://<db_user>:<db_password>@mysql-<account>.alwaysdata.net:3306/<db_name>`
- `CORS_ORIGINS=https://<frontend-address>`
- `PORT` should be read if provided by the host or used locally for fallback

## 2) Recommended alwaysdata setup

### Backend site
- Site type: **User program**
- Working directory: your uploaded `backend/` directory
- Suggested command:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

If `$PORT` is not available in the interface environment, use the port shown by alwaysdata in the User Program explanatory text.

### Frontend site
- Site type: **Static files**
- Root directory: the Angular production build directory containing `index.html`

### Database
- Create the database and DB user in the alwaysdata admin panel.
- Use MariaDB/MySQL credentials in `DATABASE_URL`.

## 3) Suggested deployment sequence
1. Create alwaysdata account.
2. Create database and database user.
3. Upload repository files by SSH/SFTP.
4. Install Python dependencies in the backend environment.
5. Configure backend User Program site.
6. Upload Angular production build output.
7. Configure frontend Static Files site.
8. Set production env vars.
9. Open `/health` on the backend and confirm 200 OK.
10. Test login, register, goal setup, workout flow, and progress pages from the frontend.

## 4) Known repo-specific deployment risks found during review
- `backend/app/config/settings.py` imports `pydantic_settings`, but `backend/requirements.txt` currently does not list `pydantic-settings`.
- `backend/app/config/database.py` currently uses `echo=True`, which should be disabled for production.
- `backend/app/config/settings.py` currently defaults CORS to localhost URLs only, so production origins need to be handled explicitly.

## 5) Minimal success criteria
- Backend boots on alwaysdata with no import errors.
- Backend connects to MySQL successfully.
- Frontend loads over HTTPS.
- Auth works end to end.
- Protected API calls work from the frontend with no CORS failures.
- Workout and progress pages do not log the user out unexpectedly.
