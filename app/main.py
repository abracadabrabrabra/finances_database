from fastapi import FastAPI
from app.routers import health_router

app = FastAPI(
    title="My API",
    description="RESTful API finances",
    version="1.0.0"
)

app.include_router(health_router)


@app.get("/")
async def root():
    return {"message": "Welcome to My API", "docs_url": "/docs"}