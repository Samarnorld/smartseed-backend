# app/api/endpoints/soil_tiles.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import ee

from app.services.gee.soil_tiles import get_multi_soil_tiles

router = APIRouter()

class SoilTilesRequest(BaseModel):
    geometry: dict
    datasets: List[str]
    depth: str = "0-20cm"


@router.post("/soil/tiles")
def soil_tiles(request: SoilTilesRequest):
    try:
        print("Fetching fresh soil tiles (NO CACHE)")

        ee_geometry = ee.Geometry(request.geometry)

        tiles = get_multi_soil_tiles(
            ee_geometry,
            request.datasets,
            request.depth
        )

        return tiles

    except Exception as e:
        print("Soil tiles error:", str(e))
        return {
            "status": "error",
            "message": str(e)
        }