# app/api/endpoints/rainfall_climatology.py
from fastapi import APIRouter, Depends
import ee

from app.api.deps import get_geometry
from app.services.gee.rainfall_climatology import (
    get_monthly_climatology,
    get_annual_climatology
)
from app.services.cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
    CACHE_90_DAYS
)

router = APIRouter(
    prefix="/rainfall/climatology",
    tags=["Rainfall Climatology"]
)

@router.post("/monthly")
def monthly_climatology(
    geometry: ee.Geometry = Depends(get_geometry)
):
    payload = {
        "geometry": geometry.getInfo()
    }
    cache_key = build_cache_key("monthly_climatology", payload)
    cached = get_cache(cache_key)
    if cached:
        print("REDIS CACHE HIT: monthly_climatology")
        return cached

    print("REDIS CACHE MISS: monthly_climatology")
    data = get_monthly_climatology(geometry)
    response = {
        "status": "success",
        "dataset": "CHIRPS",
        "units": "mm",
        **data
    }
    set_cache(cache_key, response, CACHE_90_DAYS)
    return response
    
@router.post("/annual")
def annual_climatology(
    geometry: ee.Geometry = Depends(get_geometry)
):
    payload = {
        "geometry": geometry.getInfo()
    }
    cache_key = build_cache_key("annual_climatology", payload)
    cached = get_cache(cache_key)
    if cached:
        print("REDIS CACHE HIT: annual_climatology")
        return cached
    print("REDIS CACHE MISS: annual_climatology")
    data = get_annual_climatology(geometry)
    response = {
        "status": "success",
        "dataset": "CHIRPS",
        "units": "mm",
        **data
    }
    set_cache(cache_key, response, CACHE_90_DAYS)
    return response