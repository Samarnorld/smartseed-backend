# app/api/endpoints/temperature_tiles.py
from fastapi import APIRouter, Depends, Query
import ee

from app.api.deps import get_geometry
from app.services.gee.temperature_tiles import get_temperature_tiles
from app.services.cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
    CACHE_7_DAYS
)

router = APIRouter(
    prefix="/temperature/tiles",
    tags=["Temperature Raster"]
)

@router.post("")
def temperature_tiles(
    geometry: ee.Geometry = Depends(get_geometry),
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    payload = {
        "geometry": geometry.getInfo(),
        "start_date": start_date,
        "end_date": end_date
    }
    cache_key = build_cache_key("temperature_tiles", payload)
    cached = get_cache(cache_key)
    if cached:
        print("REDIS CACHE HIT: temperature_tiles")
        return cached
    print("REDIS CACHE MISS: temperature_tiles")
    tiles = get_temperature_tiles(
        geometry=geometry,
        start_date=start_date,
        end_date=end_date
    )
    result = {
        "status": "success",
        "dataset": "ERA5-Land Daily Aggregated",
        "units": "°C",
        **tiles
    }
    set_cache(cache_key, result, CACHE_7_DAYS)
    return result