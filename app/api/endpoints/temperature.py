# app/api/endpoints/temperature.py
from fastapi import APIRouter, Depends
import ee
from app.api.deps import get_geometry
from app.services.gee.temperature import get_temperature_summary

router = APIRouter(
    prefix="/temperature",
    tags=["Temperature"]
)

@router.post("/summary")
def temperature_summary(
    geometry: ee.Geometry = Depends(get_geometry),
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31"
):

    temp = get_temperature_summary(
        geometry=geometry,
        start_date=start_date,
        end_date=end_date
    )

    return {
        "status": "success",
        "temperature": temp,
        "units": "°C",
        "dataset": "ERA5-Land"
    }
