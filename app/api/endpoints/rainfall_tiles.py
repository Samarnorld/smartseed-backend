# app/api/endpoints/rainfall_tiles.py
import logging
from fastapi import APIRouter, Depends, Query, Request, HTTPException
import ee

from app.core.limiter import limiter
from app.api.deps import get_current_user, get_geometry
from app.services.gee.rainfall_tiles import get_rainfall_tiles
from app.services.cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
    CACHE_1_HOUR
)

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/rainfall/tiles",
    tags=["Rainfall Raster"]
)

@router.post("")
@limiter.limit("10/minute")
def rainfall_tiles(request: Request,
    geometry: ee.Geometry = Depends(get_geometry),
    start_date: str = Query(...),
    end_date: str = Query(...),
    user: dict = Depends(get_current_user)
):
    try:
        payload = {
            "geometry": geometry.getInfo(),
            "start_date": start_date,
            "end_date": end_date
        }
        cache_key = build_cache_key("rainfall_tiles", payload)
        cached = get_cache(cache_key)
        if cached:
            logger.info(f"Cache HIT: rainfall_tiles for {user.get('uid')}")
            return cached

        logger.info(f"Cache MISS: rainfall_tiles for {user.get('uid')}")
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
        set_cache(cache_key, result, CACHE_1_HOUR)
        return result
    except Exception as e:
        logger.error("Rainfall tiles endpoint failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate rainfall tiles")
