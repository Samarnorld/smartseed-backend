# app/api/endpoints/soil_tiles.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import ee

from app.services.gee.soil_tiles import get_multi_soil_tiles
from app.services.cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
    CACHE_1_HOUR
)

router = APIRouter()
class SoilTilesRequest(BaseModel):
    geometry: dict
    datasets: List[str]
    depth: str = "0-20cm"

@router.post("/soil/tiles")
def soil_tiles(request: SoilTilesRequest):
    payload = {
        "geometry": request.geometry,
        "datasets": request.datasets,
        "depth": request.depth
    }
    cache_key = build_cache_key("soil_tiles", payload)
    cached = get_cache(cache_key)
    if cached:
        print("REDIS CACHE HIT: soil_tiles")
        return cached
    print("REDIS CACHE MISS: soil_tiles")
    ee_geometry = ee.Geometry(request.geometry)
    tiles = get_multi_soil_tiles(
        ee_geometry,
        request.datasets,
        request.depth
    )
    set_cache(cache_key, tiles, CACHE_1_HOUR)
    return tiles