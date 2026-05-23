from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.models_views import UserFinancialSummary, GoalProgress


class ViewCRUD:
    @staticmethod
    def get_user_financial_summary(db: Session) -> List[UserFinancialSummary]:
        try:
            db.execute(text("SELECT 1 FROM user_financial_summary LIMIT 1"))
            return db.query(UserFinancialSummary).all()
        except Exception as e:
            print(f"Warning: View 'user_financial_summary' not found: {e}")
            return []

    @staticmethod
    def get_goal_progress(db: Session) -> List[GoalProgress]:
        try:
            db.execute(text("SELECT 1 FROM goal_progress LIMIT 1"))
            return db.query(GoalProgress).all()
        except Exception as e:
            print(f"Warning: View 'goal_progress' not found: {e}")
            return []