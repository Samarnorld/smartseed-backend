# app/api/endpoints/temperature_monthly.py
from fastapi import APIRouter, Depends, Query
from datetime import datetime
import ee

from app.api.deps import get_geometry
from app.services.gee.temperature_monthly import get_monthly_temperature
from app.services.cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
    CACHE_7_DAYS
)

router = APIRouter(prefix="/temperature/monthly", tags=["Temperature"])

current_year = datetime.utcnow().year

@router.post("/")
def monthly_temperature(
    geometry: ee.Geometry = Depends(get_geometry),
    year: int = Query(..., ge=1981, le=current_year)
):
    payload = {
        "geometry": geometry.getInfo(),
        "year": year
    }
    cache_key = build_cache_key("monthly_temperature", payload)
    cached = get_cache(cache_key)
    if cached:
        print("REDIS CACHE HIT: monthly_temperature")
        return cached
    print("REDIS CACHE MISS: monthly_temperature")
    data = get_monthly_temperature(geometry=geometry, year=year)
    result = {
        "status": "success",
        "dataset": "ERA5-Land",
        "units": "°C",
        "year": year,
        "monthly": data
    }
    set_cache(cache_key, result, CACHE_7_DAYS)
    return result