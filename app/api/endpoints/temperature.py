# app/api/endpoints/temperature.py
from fastapi import APIRouter, Depends
import ee
from app.api.deps import get_geometry
from app.services.gee.temperature import get_temperature_summary
from app.services.cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
    CACHE_7_DAYS
)

router = APIRouter(
    prefix="/temperature",
    tags=["Temperature"]
)

@router.post("/summary")
def temperature_summary(
    geometry: ee.Geometry = Depends(get_geometry),
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31"
):
    payload = {
        "geometry": geometry.getInfo(),
        "start_date": start_date,
        "end_date": end_date
    }
    cache_key = build_cache_key("temperature_summary", payload)
    cached = get_cache(cache_key)
    if cached:
        print("REDIS CACHE HIT: temperature_summary")
        return cached
    print("REDIS CACHE MISS: temperature_summary")
    temp = get_temperature_summary(
        geometry=geometry,
        start_date=start_date,
        end_date=end_date
    )
    result = {
        "status": "success",
        "temperature": temp,
        "units": "°C",
        "dataset": "ERA5-Land"
    }
    set_cache(cache_key, result, CACHE_7_DAYS)
    return result