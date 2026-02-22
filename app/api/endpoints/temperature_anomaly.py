# app/api/endpoints/temperature_anomaly.py
from fastapi import APIRouter, Depends, Query
from datetime import datetime
import ee

from app.api.deps import get_geometry
from app.services.gee.temperature_anomaly import (
    get_current_season_overview,
    get_temperature_seasonal_anomaly,
    get_10yr_temperature_trend,
    get_agronomic_interpretation
)

router = APIRouter(prefix="/temperature", tags=["Temperature"])

current_year = datetime.utcnow().year


@router.post("/dashboard")
def temperature_dashboard(
    season: str = Query(..., description="MAM, JJA, SON, DJF"),
    year: int = Query(..., ge=1981, le=current_year),
    geometry: ee.Geometry = Depends(get_geometry)
):

    overview = get_current_season_overview(geometry, season, year)

    anomaly = get_temperature_seasonal_anomaly(geometry, season, year)

    trend = get_10yr_temperature_trend(geometry, season, year)

    agronomic = get_agronomic_interpretation(
        mean_temp_c=overview["mean_temp_c"],
        heat_days=overview["heat_stress_days_above_35C"]
    )

    return {
        "status": "success",
        "dataset": "ERA5-Land",
        "units": "°C",
        "section_a_overview": overview,
        "section_b_anomaly": anomaly,
        "section_c_trend": trend,
        "section_d_agronomic_interpretation": agronomic
    }