from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check():
    return {"status": "ok", "message": "Service is running"}


@router.get("/db")
async def db_health_check():
    return {"status": "ok", "database": "not_configured_yet"}