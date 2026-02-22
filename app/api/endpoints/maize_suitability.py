# app/api/endpoints/maize_suitability.py
from fastapi import APIRouter
from pydantic import BaseModel
import ee
from app.services.gee.maize_suitability import compute_maize_suitability

router = APIRouter(tags=["Maize Suitability"])

class SuitabilityRequest(BaseModel):
    geometry: dict
    year: int
    season: str
    depth: str = "0-20cm"

@router.post("/maize/suitability")
def maize_suitability(request: SuitabilityRequest):
    ee_geometry = ee.Geometry(request.geometry)

    return compute_maize_suitability(
        geometry=ee_geometry,
        year=request.year,
        season=request.season,
        depth=request.depth
    )