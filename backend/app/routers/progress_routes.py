from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.models import User, ProgressLog
from app.schemas.schemas import ProgressLogCreate, ProgressLogResponse
from app.routers.user_routes import get_current_user

router = APIRouter(prefix="/progress", tags=["progress"])


@router.post("/log", response_model=ProgressLogResponse, status_code=status.HTTP_201_CREATED)
async def log_progress(
    progress_data: ProgressLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log user's weight and body fat progress"""
    
    new_log = ProgressLog(
        user_id=current_user.id,
        weight_kg=progress_data.weight_kg,
        body_fat_percentage=progress_data.body_fat_percentage,
        notes=progress_data.notes
    )
    
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    
    return new_log


@router.get("/logs", response_model=list[ProgressLogResponse])
async def get_progress_logs(
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's progress logs with limit"""
    
    logs = db.query(ProgressLog).filter(
        ProgressLog.user_id == current_user.id
    ).order_by(ProgressLog.logged_at.desc()).limit(limit).all()
    
    return logs


@router.get("/summary")
async def get_progress_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress summary (latest log, weight change, etc.)"""
    
    logs = db.query(ProgressLog).filter(
        ProgressLog.user_id == current_user.id
    ).order_by(ProgressLog.logged_at.desc()).limit(2).all()
    
    if not logs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No progress logs found"
        )
    
    summary = {
        "latest_log": logs[0],
        "weight_change": None,
        "body_fat_change": None
    }
    
    if len(logs) >= 2:
        weight_diff = logs[0].weight_kg - logs[1].weight_kg
        summary["weight_change"] = round(weight_diff, 1)
        
        if logs[0].body_fat_percentage and logs[1].body_fat_percentage:
            bf_diff = logs[0].body_fat_percentage - logs[1].body_fat_percentage
            summary["body_fat_change"] = round(bf_diff, 1)
    
    return summary
