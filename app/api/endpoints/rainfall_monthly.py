# app/api/endpoints/rainfall_monthly.py
from fastapi import APIRouter, Depends, Query
import ee

from app.api.deps import get_geometry
from app.services.gee.rainfall_monthly import get_monthly_rainfall

router = APIRouter(prefix="/rainfall", tags=["Rainfall"])

@router.post("/monthly")
def monthly_rainfall(
    geometry: ee.Geometry = Depends(get_geometry),
    year: int = Query(..., ge=1981)
):

    data = get_monthly_rainfall(
    geometry=geometry,
    year=year
)

    return {
        "status": "success",
        "dataset": "CHIRPS",
        "units": "mm",
        "monthly_rainfall": data
    }
