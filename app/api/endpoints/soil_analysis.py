# app/api/endpoints/soil_analysis.py
from fastapi import APIRouter, Body
import ee
from app.services.gee.soil_raw import get_raw_soil_data
from app.services.gee.soil_intelligence import build_soil_intelligence
from app.services.cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
    CACHE_30_DAYS
)

router = APIRouter()

@router.post("/soil/analysis")
def soil_analysis(
    geometry: dict = Body(...),
    depth: str = "0-20cm",
):
    payload = {
        "geometry": geometry,
        "depth": depth
    }
    cache_key = build_cache_key("soil_analysis", payload)
    cached = get_cache(cache_key)
    if cached:
        print("REDIS CACHE HIT: soil_analysis")
        return cached

    print("REDIS CACHE MISS: soil_analysis")
    ee_geometry = ee.Geometry(geometry)
    raw = get_raw_soil_data(ee_geometry, depth)
    if raw["status"] != "success":
        return raw
    intelligence = build_soil_intelligence(raw["soil_profile"])
    result = {
        "status": "success",
        "depth": depth,
        "soil_intelligence": intelligence,
    }
    set_cache(cache_key, result, CACHE_30_DAYS)
    return result