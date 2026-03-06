# app/api/endpoints/rainfall.py
from fastapi import APIRouter, Depends, Query
import ee

from app.api.deps import get_geometry
from app.services.gee.rainfall import (
    compute_rainfall,
    get_annual_rainfall
)
from app.services.cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
    CACHE_7_DAYS
)

router = APIRouter(
    prefix="/rainfall",
    tags=["Rainfall"]
)

# Custom Date Range
@router.post("/analyze")
def rainfall_analysis(
    geometry: ee.Geometry = Depends(get_geometry),
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    payload = {
        "geometry": geometry.getInfo(),
        "start_date": start_date,
        "end_date": end_date
    }
    cache_key = build_cache_key("rainfall_analysis", payload)
    cached = get_cache(cache_key)
    if cached:
        print("REDIS CACHE HIT: rainfall_analysis")
        return cached
    print("REDIS CACHE MISS: rainfall_analysis")
    rainfall = compute_rainfall(
        geometry=geometry,
        start_date=start_date,
        end_date=end_date
    )
    result = {
        "status": "success",
        "rainfall": rainfall,
        "units": "mm",
        "dataset": "CHIRPS"
    }
    set_cache(cache_key, result, CACHE_7_DAYS)
    return result

# Annual Rainfall
@router.post("/annual")
def annual_rainfall(
    geometry: ee.Geometry = Depends(get_geometry),
    year: int = Query(..., ge=1981)
):
    payload = {
        "geometry": geometry.getInfo(),
        "year": year
    }
    cache_key = build_cache_key("annual_rainfall", payload)
    cached = get_cache(cache_key)
    if cached:
        print("REDIS CACHE HIT: annual_rainfall")
        return cached
    print("REDIS CACHE MISS: annual_rainfall")
    result = get_annual_rainfall(
        geometry=geometry,
        year=year
    )
    response = {
        "status": "success",
        "dataset": "CHIRPS",
        "units": "mm",
        **result
    }
    set_cache(cache_key, response, CACHE_7_DAYS)
    return response