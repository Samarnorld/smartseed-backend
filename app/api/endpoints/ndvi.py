# app/api/endpoints/ndvi.py
from fastapi import APIRouter, Depends, Query
import ee
from app.api.deps import get_geometry
from app.services.gee.ndvi import get_ndvi_summary, get_ndvi_timeseries

router = APIRouter(prefix="/ndvi", tags=["NDVI"])

@router.post("/summary")
def ndvi_summary(
    geometry: ee.Geometry = Depends(get_geometry),
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    return get_ndvi_summary(geometry, start_date, end_date)

@router.post("/timeseries")
def ndvi_timeseries(
    geometry: ee.Geometry = Depends(get_geometry),
    start_year: int = Query(...),
    end_year: int = Query(...)
):
    return get_ndvi_timeseries(geometry, start_year, end_year)