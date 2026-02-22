# app/api/endpoints/gee.py
from fastapi import APIRouter
import ee

router = APIRouter(
    prefix="/gee",
    tags=["Google Earth Engine"]
)

@router.get("/health")
def gee_health():
    """
    Fast health check: confirms EE auth + basic access
    """
    image = ee.ImageCollection("COPERNICUS/S2_SR").first()
    info = image.getInfo()

    return {
        "gee": "connected",
        "sample_image_type": info["type"]
    }
