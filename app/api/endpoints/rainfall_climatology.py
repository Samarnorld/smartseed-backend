# app/api/endpoints/rainfall_climatology.py
from fastapi import APIRouter, Depends
import ee

from app.api.deps import get_geometry
from app.services.gee.rainfall_climatology import (
    get_monthly_climatology,
    get_annual_climatology
)

router = APIRouter(
    prefix="/rainfall/climatology",
    tags=["Rainfall Climatology"]
)

@router.post("/monthly")
def monthly_climatology(
    geometry: ee.Geometry = Depends(get_geometry)
):
    data = get_monthly_climatology(geometry)

    return {
        "status": "success",
        "dataset": "CHIRPS",
        "units": "mm",
        **data
    }

@router.post("/annual")
def annual_climatology(
    geometry: ee.Geometry = Depends(get_geometry)
):
    data = get_annual_climatology(geometry)

    return {
        "status": "success",
        "dataset": "CHIRPS",
        "units": "mm",
        **data
    }