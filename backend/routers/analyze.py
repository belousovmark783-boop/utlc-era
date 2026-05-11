"""
Анализ маршрутов: POST /api/analyze, GET /api/stats
"""
import csv
import io

from fastapi import APIRouter, HTTPException

from db.database import get_total_count, save_analysis, save_analysis_results
from schemas.analysis import AnalyzeRequest
from services.tco import calculate_tco, calculate_score

router = APIRouter()


@router.get("/stats")
def stats():
    return {"total_analyses": get_total_count()}


@router.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        reader = csv.DictReader(io.StringIO(req.csv_content))
        rows = list(reader)
    except Exception as e:
        raise HTTPException(400, f"CSV parse error: {e}")

    if not rows:
        raise HTTPException(400, "CSV is empty")

    tco_data = []
    for row in rows:
        t = calculate_tco(row, req.cargo_value, req.capital_rate)
        tco_data.append({**row, **t})

    all_tcos      = [r["total"]        for r in tco_data]
    all_days      = [r["transit_days"] for r in tco_data]
    all_risks     = [r["risk_index"]   for r in tco_data]
    all_emissions = [r["emissions"]    for r in tco_data]

    w = req.weights.model_dump()
    results = []
    for r in tco_data:
        score = calculate_score(
            r["total"], r["transit_days"], r["risk_index"], r["emissions"],
            w, all_tcos, all_days, all_risks, all_emissions
        )
        results.append({
            "route_id":    r.get("route_id", ""),
            "mode":        r.get("mode", ""),
            "origin":      r.get("origin", ""),
            "destination": r.get("destination", ""),
            "cost_usd":    r["total"],
            "time_days":   r["transit_days"],
            "risk_index":  r["risk_index"],
            "emissions":   r["emissions"],
            "score":       score,
            "breakdown": {
                "base":        r["base_cost"],
                "customs":     r["customs"],
                "handling":    r["handling"],
                "carbon":      r["carbon"],
                "insurance":   r["insurance"],
                "working_cap": r["working_cap"],
                "inventory":   r["inventory"],
                "admin":       r["admin"],
                "contingency": r["contingency"],
            },
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    analysis_id = save_analysis(results, w, req.cargo_value, req.capital_rate)
    save_analysis_results(analysis_id, results)

    return {
        "id": analysis_id,
        "results": results,
        "weights": w,
        "cargo_value": req.cargo_value,
        "capital_rate": req.capital_rate,
    }
