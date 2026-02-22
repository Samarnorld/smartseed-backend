# app/services/gee/maize_timeseries.py
from app.services.gee.maize_suitability import compute_maize_suitability

def maize_time_series(geometry, start_year, end_year, season):

    results = []

    for year in range(start_year, end_year + 1):
        data = compute_maize_suitability(geometry, year, season)
        results.append({
            "year": year,
            "score": data["final_suitability_score"]
        })

    return results