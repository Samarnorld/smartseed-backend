# app/api/endpoints/rainfall_anomaly.py
from fastapi import APIRouter, Depends, Query
import ee

from app.api.deps import get_geometry
from app.services.gee.rainfall_anomaly import (
    get_seasonal_anomaly,
    get_annual_anomaly,
    get_monthly_anomaly,
)

router = APIRouter(prefix="/rainfall", tags=["Rainfall Anomaly"])

# SEASONAL (MAM / OND)
@router.post("/anomaly/seasonal")
def seasonal_anomaly(
    geometry: ee.Geometry = Depends(get_geometry),
    year: int = Query(..., ge=1981),
    season: str = Query(..., description="long_rains or short_rains"),
):
    result = get_seasonal_anomaly(geometry, year, season)

    return {
        "dataset": "CHIRPS",
        "units": "mm",
        **result
    }

# ANNUAL
@router.post("/anomaly/annual")
def annual_anomaly(
    geometry: ee.Geometry = Depends(get_geometry),
    year: int = Query(..., ge=1981),
):
    result = get_annual_anomaly(geometry, year)

    return {
        "dataset": "CHIRPS",
        "units": "mm",
        **result
    }

# MONTHLY
@router.post("/anomaly/monthly")
def monthly_anomaly(
    geometry: ee.Geometry = Depends(get_geometry),
    year: int = Query(..., ge=1981),
    month: int = Query(..., ge=1, le=12),
):
    result = get_monthly_anomaly(geometry, year, month)

    return {
        "dataset": "CHIRPS",
        "units": "mm",
        **result
    }