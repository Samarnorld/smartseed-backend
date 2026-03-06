# app/api/endpoints/rainfall_monthly.py
from fastapi import APIRouter, Depends, Query
import ee

from app.api.deps import get_geometry
from app.services.gee.rainfall_monthly import get_monthly_rainfall
from app.services.cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
    CACHE_7_DAYS
)

router = APIRouter(prefix="/rainfall", tags=["Rainfall"])

@router.post("/monthly")
def monthly_rainfall(
    geometry: ee.Geometry = Depends(get_geometry),
    year: int = Query(..., ge=1981)
):
    payload = {
        "geometry": geometry.getInfo(),
        "year": year
    }
    cache_key = build_cache_key("monthly_rainfall", payload)
    cached = get_cache(cache_key)
    if cached:
        print("REDIS CACHE HIT: monthly_rainfall")
        return cached
    print("REDIS CACHE MISS: monthly_rainfall")
    data = get_monthly_rainfall(
        geometry=geometry,
        year=year
    )
    result = {
        "status": "success",
        "dataset": "CHIRPS",
        "units": "mm",
        "monthly_rainfall": data
    }
    set_cache(cache_key, result, CACHE_7_DAYS)
    return result