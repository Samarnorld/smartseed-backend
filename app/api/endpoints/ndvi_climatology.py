# app/api/endpoints/ndvi_climatology.py
from fastapi import APIRouter, Depends
import ee
from app.api.deps import get_geometry
from app.services.gee.ndvi_climatology import get_ndvi_climatology

router = APIRouter(prefix="/ndvi", tags=["NDVI"])

@router.post("/climatology")
def ndvi_climatology(
    geometry: ee.Geometry = Depends(get_geometry)
):
    return get_ndvi_climatology(geometry)