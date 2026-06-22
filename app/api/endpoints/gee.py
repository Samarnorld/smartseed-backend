# app/api/endpoints/gee.py
from fastapi import APIRouter
import ee

router = APIRouter(
    prefix="/gee",
    tags=["Google Earth Engine"]
)

@router.get("/health")
def gee_health():

    try:
        ee.Number(1).getInfo()

        return {
            "status": "healthy"
        }

    except Exception:
        return {
            "status": "unhealthy"
        }