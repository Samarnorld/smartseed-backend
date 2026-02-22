# app/api/endpoints/ndvi_anomaly.py
from fastapi import APIRouter, Depends, Query
import ee
from app.api.deps import get_geometry
from app.services.gee.ndvi_anomaly import get_seasonal_anomaly
router = APIRouter(prefix="/ndvi", tags=["NDVI"])
@router.post("/anomaly")
def ndvi_anomaly(
    geometry: ee.Geometry = Depends(get_geometry),
    year: int = Query(...),
    season: str = Query(...)
):
    return get_seasonal_anomaly(geometry, year, season)