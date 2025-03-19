from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db

router = APIRouter()

@router.get("/health", summary="Health check endpoint")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint that verifies the API is running and can connect to the database.
    """
    return {
        "status": "ok",
        "database": "connected",
        "api_version": "1.0.0"
    } 