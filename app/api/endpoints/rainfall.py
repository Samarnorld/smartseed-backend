# app/api/endpoints/rainfall.py
from fastapi import APIRouter, Depends, Query
import ee

from app.api.deps import get_geometry
from app.services.gee.rainfall import (
    compute_rainfall,
    get_annual_rainfall
)

router = APIRouter(
    prefix="/rainfall",
    tags=["Rainfall"]
)

# Custom Date Range
@router.post("/analyze")
def rainfall_analysis(
    geometry: ee.Geometry = Depends(get_geometry),
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD")
):
    rainfall = compute_rainfall(
        geometry=geometry,
        start_date=start_date,
        end_date=end_date
    )

    return {
        "status": "success",
        "rainfall": rainfall,
        "units": "mm",
        "dataset": "CHIRPS"
    }

# Annual Rainfall
@router.post("/annual")
def annual_rainfall(
    geometry: ee.Geometry = Depends(get_geometry),
    year: int = Query(..., ge=1981)
):
    result = get_annual_rainfall(
        geometry=geometry,
        year=year
    )

    return {
        "status": "success",
        "dataset": "CHIRPS",
        "units": "mm",
        **result
    }