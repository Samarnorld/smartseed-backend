# app/api/endpoints/soil_analysis.py
from fastapi import APIRouter, Body
import ee

from app.services.gee.soil_raw import get_raw_soil_data
from app.services.gee.soil_intelligence import build_soil_intelligence

router = APIRouter()

@router.post("/soil/analysis")
def soil_analysis(
    geometry: dict = Body(...),
    depth: str = "0-20cm",
):
    ee_geometry = ee.Geometry(geometry)

    raw = get_raw_soil_data(ee_geometry, depth)

    if raw["status"] != "success":
        return raw

    intelligence = build_soil_intelligence(raw["soil_profile"])

    return {
        "status": "success",
        "depth": depth,
        "soil_intelligence": intelligence,
    }