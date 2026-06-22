# app/api/endpoints/temperature_monthly.py
import logging
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from datetime import datetime
import ee

from app.core.limiter import limiter
from app.api.deps import get_current_user, get_geometry
from app.services.gee.temperature_monthly import get_monthly_temperature
from app.services.cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
    CACHE_7_DAYS
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/temperature/monthly", tags=["Temperature"])
current_year = datetime.utcnow().year

@router.post("/")
@limiter.limit("20/minute")
def monthly_temperature(request: Request,
    geometry: ee.Geometry = Depends(get_geometry),
    year: int = Query(..., ge=1981, le=current_year),
    user: dict = Depends(get_current_user)
):
    try:
        payload = {
            "geometry": geometry.getInfo(),
            "year": year
        }
        cache_key = build_cache_key("monthly_temperature", payload)
        cached = get_cache(cache_key)
        if cached:
            logger.info(f"Cache HIT: monthly_temperature for {user.get('uid')}")
            return cached

        logger.info(f"Cache MISS: monthly_temperature for {user.get('uid')}")
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
    except Exception as e:
        logger.error("Monthly temperature endpoint failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
