"""
История анализов: GET /api/history, GET /api/analysis/{id}, DELETE /api/analysis/{id}
"""
from fastapi import APIRouter, HTTPException

from db.database import get_all_analyses, get_analysis_by_id, delete_analysis_by_id

router = APIRouter()


@router.get("/history")
def history(limit: int = 50, offset: int = 0):
    return get_all_analyses(limit, offset)


@router.get("/analysis/{analysis_id}")
def get_analysis(analysis_id: int):
    a = get_analysis_by_id(analysis_id)
    if not a:
        raise HTTPException(404, "Analysis not found")
    return a


@router.delete("/analysis/{analysis_id}")
def delete_analysis(analysis_id: int):
    deleted = delete_analysis_by_id(analysis_id)
    if not deleted:
        raise HTTPException(404, "Analysis not found")
    return {"deleted": analysis_id}
