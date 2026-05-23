from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Dict, Any
from datetime import date
from decimal import Decimal


class ReportsCRUD:
    @staticmethod
    def get_transactions_per_day(db: Session, limit: int = 30) -> List[Dict[str, Any]]:
        query = text("""
            SELECT 
                transaction_date,
                COUNT(*) as transactions_per_day
            FROM transactions
            GROUP BY transaction_date
            ORDER BY transaction_date DESC
            LIMIT :limit
        """)

        result = db.execute(query, {"limit": limit})
        return [{"transaction_date": row[0], "transactions_per_day": row[1]} for row in result]

    @staticmethod
    def get_user_transaction_stats(db: Session) -> List[Dict[str, Any]]:
        query = text("""
            SELECT 
                u.email,
                MIN(t.transaction_date) as first_transaction,
                MAX(t.transaction_date) as last_transaction,
                MIN(t.amount) as smallest_amount,
                MAX(t.amount) as largest_amount
            FROM transactions t
                JOIN accounts a ON a.id = t.account_id
                JOIN users u ON u.id = a.user_id
            GROUP BY u.email
            ORDER BY u.email
        """)

        result = db.execute(query)
        return [
            {
                "email": row[0],
                "first_transaction": row[1],
                "last_transaction": row[2],
                "smallest_amount": row[3],
                "largest_amount": row[4]
            }
            for row in result
        ]

    @staticmethod
    def get_import_statistics_aggregated(db: Session) -> Dict[str, Any]:
        query = text("""
            SELECT 
                AVG(rows_processed) as avg_rows_processed,
                AVG(rows_succeeded) as avg_rows_succeeded,
                AVG(CASE 
                    WHEN rows_processed > 0 
                    THEN CAST(rows_succeeded AS FLOAT) / rows_processed * 100 
                    ELSE 0 
                END) as avg_success_rate
            FROM import_logs
            WHERE rows_processed > 0
        """)

        result = db.execute(query).first()

        return {
            "avg_rows_processed": float(result[0]) if result[0] else None,
            "avg_rows_succeeded": float(result[1]) if result[1] else None,
            "avg_success_rate": float(result[2]) if result[2] else None
        }

    @staticmethod
    def get_category_expenses(db: Session, user_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            SELECT 
                c.name as category_name,
                COALESCE(SUM(t.amount), 0) as total_expenses
            FROM categories c
                LEFT JOIN transactions t ON t.category_id = c.id AND t.type = 'expense'
        """

        params = {}
        if user_id:
            query += " WHERE c.user_id = :user_id"
            params["user_id"] = user_id

        query += " GROUP BY c.name ORDER BY total_expenses DESC LIMIT :limit"
        params["limit"] = limit

        result = db.execute(text(query), params)
        return [{"category_name": row[0], "total_expenses": float(row[1])} for row in result]

    @staticmethod
    def get_monthly_income_expense(db: Session, year: int = None) -> List[Dict[str, Any]]:
        year_condition = ""
        params = {}

        if year:
            year_condition = " AND EXTRACT(YEAR FROM t.transaction_date) = :year"
            params["year"] = year

        query = text(f"""
            SELECT 
                DATE_TRUNC('month', t.transaction_date) as month,
                COALESCE(SUM(CASE WHEN t.type = 'income' THEN t.amount ELSE 0 END), 0) as total_income,
                COALESCE(SUM(CASE WHEN t.type = 'expense' THEN t.amount ELSE 0 END), 0) as total_expense
            FROM transactions t
            WHERE 1=1 {year_condition}
            GROUP BY DATE_TRUNC('month', t.transaction_date)
            ORDER BY month DESC
            LIMIT 12
        """)

        result = db.execute(query, params)
        return [
            {
                "month": row[0].strftime("%Y-%m") if row[0] else None,
                "total_income": float(row[1]),
                "total_expense": float(row[2]),
                "net": float(row[1] - row[2])
            }
            for row in result
        ]