# app/api/endpoints/temperature_monthly.py
from fastapi import APIRouter, Depends, Query
from datetime import datetime
import ee

from app.api.deps import get_geometry
from app.services.gee.temperature_monthly import get_monthly_temperature

router = APIRouter(prefix="/temperature/monthly", tags=["Temperature"])

current_year = datetime.utcnow().year


@router.post("/")
def monthly_temperature(
    geometry: ee.Geometry = Depends(get_geometry),
    year: int = Query(..., ge=1981, le=current_year)
):

    data = get_monthly_temperature(geometry=geometry, year=year)

    return {
        "status": "success",
        "dataset": "ERA5-Land",
        "units": "°C",
        "year": year,
        "monthly": data
    }