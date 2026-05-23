from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.crud.reports import ReportsCRUD
from app.schemas import (
    TransactionsPerDayResponse,
    UserTransactionStatsResponse,
    ImportStatsResponse
)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/transactions-per-day", response_model=List[TransactionsPerDayResponse])
def get_transactions_per_day(
        limit: int = Query(30, ge=1, le=365, description="Num of days"),
        db: Session = Depends(get_db)
):
    try:
        result = ReportsCRUD.get_transactions_per_day(db, limit)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch transactions per day: {str(e)}"
        )


@router.get("/user-transaction-stats", response_model=List[UserTransactionStatsResponse])
def get_user_transaction_stats(db: Session = Depends(get_db)):
    try:
        result = ReportsCRUD.get_user_transaction_stats(db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user transaction stats: {str(e)}"
        )


@router.get("/import-stats", response_model=ImportStatsResponse)
def get_import_stats_aggregated(db: Session = Depends(get_db)):
    try:
        result = ReportsCRUD.get_import_statistics_aggregated(db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch import stats: {str(e)}"
        )


@router.get("/category-expenses", response_model=dict)
def get_category_expenses(
        user_id: Optional[UUID] = Query(None, description="User filter"),
        limit: int = Query(10, ge=1, le=50, description="Num of categories"),
        db: Session = Depends(get_db)
):
    try:
        result = ReportsCRUD.get_category_expenses(db, str(user_id) if user_id else None, limit)
        return {
            "total_categories": len(result),
            "expenses_by_category": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch category expenses: {str(e)}"
        )


@router.get("/monthly-dynamics", response_model=dict)
def get_monthly_dynamics(
        year: Optional[int] = Query(None, description="Year"),
        db: Session = Depends(get_db)
):
    try:
        result = ReportsCRUD.get_monthly_income_expense(db, year)
        return {
            "period": "monthly",
            "data": result,
            "summary": {
                "total_income": sum(item["total_income"] for item in result),
                "total_expense": sum(item["total_expense"] for item in result),
                "net_savings": sum(item["net"] for item in result)
            } if result else {}
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch monthly dynamics: {str(e)}"
        )