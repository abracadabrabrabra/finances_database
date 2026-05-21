from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check():
    return {"status": "ok", "message": "Service is running"}


@router.get("/db")
async def db_health_check(db: Session = Depends(get_db)):
    try:
        version_result = db.execute(text("SELECT version()")).first()

        tables_count = {}

        count_queries = {
            "users": "SELECT COUNT(*) FROM users",
            "accounts": "SELECT COUNT(*) FROM accounts",
            "categories": "SELECT COUNT(*) FROM categories",
            "transactions": "SELECT COUNT(*) FROM transactions",
            "goals": "SELECT COUNT(*) FROM goals"
        }

        for table_name, query in count_queries.items():
            try:
                result = db.execute(text(query)).first()
                tables_count[table_name] = result[0]
            except Exception as e:
                tables_count[table_name] = f"Error: {str(e)}"

        schema_check = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)).fetchall()

        tables_list = [row[0] for row in schema_check]

        return {
            "status": "ok",
            "database": "connected",
            "postgres_version": version_result[0].split(",")[0] if version_result else "unknown",
            "tables_found": len(tables_list),
            "tables_list": tables_list,
            "records_count": tables_count
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )