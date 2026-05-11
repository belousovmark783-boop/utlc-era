"""
Health check endpoint
"""
from fastapi import APIRouter
from db.database import get_total_count

router = APIRouter()


@router.get("/health")
def health_check():
    try:
        count = get_total_count()
        return {"status": "ok", "db": "ok", "analyses_count": count}
    except Exception as e:
        return {"status": "degraded", "db": "error", "detail": str(e)}
