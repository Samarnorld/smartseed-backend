# app/api/endpoints/maize_timeseries.py
from fastapi import APIRouter
from pydantic import BaseModel
import ee
from app.services.gee.maize_timeseries import maize_time_series

router = APIRouter(tags=["Maize Time Series"])

class TimeSeriesRequest(BaseModel):
    geometry: dict
    start_year: int
    end_year: int
    season: str

@router.post("/maize/timeseries")
def maize_timeseries(request: TimeSeriesRequest):

    ee_geometry = ee.Geometry(request.geometry)

    return maize_time_series(
        geometry=ee_geometry,
        start_year=request.start_year,
        end_year=request.end_year,
        season=request.season
    )