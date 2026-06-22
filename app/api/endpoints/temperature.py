# app/api/endpoints/temperature.py
import logging
from fastapi import APIRouter, Depends, Request, HTTPException
import ee

from app.core.limiter import limiter
from app.api.deps import get_current_user
from app.api.schemas import TemperatureRequest
from app.services.gee.geometry import geojson_to_ee
from app.services.gee.temperature import get_temperature_summary
from app.services.cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
    CACHE_7_DAYS
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/temperature",
    tags=["Temperature"]
)

@router.post("/summary")
@limiter.limit("20/minute")
def temperature_summary(request: Request,
    req: TemperatureRequest,
    user: dict = Depends(get_current_user)
):
    """Get temperature summary. Requires authentication."""
    try:
        geometry = geojson_to_ee(req.geometry)
        
        payload = {
            "geometry": geometry.getInfo(),
            "start_date": str(req.start_date),
            "end_date": str(req.end_date)
        }
        cache_key = build_cache_key("temperature_summary", payload)
        
        # Try cache
        if cache_key:
            cached = get_cache(cache_key)
            if cached:
                logger.info(f"Cache HIT: temperature_summary for {user.get('uid')}")
                return cached
        
        logger.info(f"Cache MISS: temperature_summary for {user.get('uid')}")
        temp = get_temperature_summary(
            geometry=geometry,
            start_date=str(req.start_date),
            end_date=str(req.end_date)
        )
        
        result = {
            "status": "success",
            "temperature": temp,
            "units": "°C",
            "dataset": "ERA5-Land"
        }
        
        # Store in cache
        if cache_key:
            set_cache(cache_key, result, CACHE_7_DAYS)
        
        return result
    except Exception as e:
        logger.error(f"Temperature analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
