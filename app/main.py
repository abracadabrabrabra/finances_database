from fastapi import FastAPI
from app.routers import (
    health_router,
    users_router,
    import_logs_router,
    categories_router,
    views_router,
    reports_router
)
from app.database import engine, Base
import os


if os.getenv("CREATE_TABLES", "false").lower() == "true":
    Base.metadata.create_all(bind=engine)
    print("Tables created (development mode)")

app = FastAPI(
    title="Personal Finance API",
    description="RESTful API finances",
    version="1.0.0"
)

app.include_router(health_router)
app.include_router(users_router)
app.include_router(import_logs_router)
app.include_router(categories_router)
app.include_router(views_router)
app.include_router(reports_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Personal Finance API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_check": "/health",
        "db_status": "/health/db"
    }