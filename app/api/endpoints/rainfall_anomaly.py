# app/api/endpoints/rainfall_anomaly.py
from fastapi import APIRouter, Depends, Query
import ee

from app.api.deps import get_geometry
from app.services.gee.rainfall_anomaly import (
    get_seasonal_anomaly,
    get_annual_anomaly,
    get_monthly_anomaly,
)
from app.services.cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
    CACHE_30_DAYS
)
router = APIRouter(prefix="/rainfall", tags=["Rainfall Anomaly"])

# SEASONAL (MAM / OND)
@router.post("/anomaly/seasonal")
def seasonal_anomaly(
    geometry: ee.Geometry = Depends(get_geometry),
    year: int = Query(..., ge=1981),
    season: str = Query(...)
):
    payload = {
        "geometry": geometry.getInfo(),
        "year": year,
        "season": season
    }
    cache_key = build_cache_key("seasonal_anomaly", payload)
    cached = get_cache(cache_key)
    if cached:
        print("REDIS CACHE HIT: seasonal_anomaly")
        return cached
    print("REDIS CACHE MISS: seasonal_anomaly")
    result = get_seasonal_anomaly(geometry, year, season)
    response = {
        "dataset": "CHIRPS",
        "units": "mm",
        **result
    }
    set_cache(cache_key, response, CACHE_30_DAYS)
    return response

# ANNUAL
@router.post("/anomaly/annual")
def annual_anomaly(
    geometry: ee.Geometry = Depends(get_geometry),
    year: int = Query(..., ge=1981),
):
    payload = {
        "geometry": geometry.getInfo(),
        "year": year
    }
    cache_key = build_cache_key("annual_anomaly", payload)
    cached = get_cache(cache_key)
    if cached:
        print("REDIS CACHE HIT: annual_anomaly")
        return cached
    print("REDIS CACHE MISS: annual_anomaly")
    result = get_annual_anomaly(geometry, year)
    response = {
        "dataset": "CHIRPS",
        "units": "mm",
        **result
    }
    set_cache(cache_key, response, CACHE_30_DAYS)
    return response

# MONTHLY
@router.post("/anomaly/monthly")
def monthly_anomaly(
    geometry: ee.Geometry = Depends(get_geometry),
    year: int = Query(..., ge=1981),
    month: int = Query(..., ge=1, le=12),
):
    payload = {
        "geometry": geometry.getInfo(),
        "year": year,
        "month": month
    }
    cache_key = build_cache_key("monthly_anomaly", payload)
    cached = get_cache(cache_key)
    if cached:
        print("REDIS CACHE HIT: monthly_anomaly")
        return cached
    print("REDIS CACHE MISS: monthly_anomaly")
    result = get_monthly_anomaly(geometry, year, month)
    response = {
        "dataset": "CHIRPS",
        "units": "mm",
        **result
    }
    set_cache(cache_key, response, CACHE_30_DAYS)
    return response