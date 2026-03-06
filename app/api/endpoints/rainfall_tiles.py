# app/api/endpoints/rainfall_tiles.py
from fastapi import APIRouter, Depends, Query
import ee

from app.api.deps import get_geometry
from app.services.gee.rainfall_tiles import get_rainfall_tiles
from app.services.cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
    CACHE_7_DAYS
)

router = APIRouter(
    prefix="/rainfall/tiles",
    tags=["Rainfall Raster"]
)

@router.post("")
def rainfall_tiles(
    geometry: ee.Geometry = Depends(get_geometry),
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    payload = {
        "geometry": geometry.getInfo(),
        "start_date": start_date,
        "end_date": end_date
    }
    cache_key = build_cache_key("rainfall_tiles", payload)
    cached = get_cache(cache_key)
    if cached:
        print("REDIS CACHE HIT: rainfall_tiles")
        return cached
    print("REDIS CACHE MISS: rainfall_tiles")
    tiles = get_rainfall_tiles(
        geometry=geometry,
        start_date=start_date,
        end_date=end_date
    )
    result = {
        "status": "success",
        "dataset": "CHIRPS",
        "units": "mm",
        **tiles
    }
    set_cache(cache_key, result, CACHE_7_DAYS)
    return result