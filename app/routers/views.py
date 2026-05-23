from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.views import ViewCRUD
from app.schemas import UserFinancialSummaryResponse, GoalProgressResponse

router = APIRouter(prefix="/views", tags=["Views"])


@router.get("/user-financial-summary", response_model=List[UserFinancialSummaryResponse])
def get_user_financial_summary(db: Session = Depends(get_db)):
    try:
        result = ViewCRUD.get_user_financial_summary(db)
        if not result:
            return []
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user financial summary: {str(e)}"
        )


@router.get("/goal-progress", response_model=List[GoalProgressResponse])
def get_goal_progress(db: Session = Depends(get_db)):
    try:
        result = ViewCRUD.get_goal_progress(db)
        if not result:
            return []
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch goal progress: {str(e)}"
        )