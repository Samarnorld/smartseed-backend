# app/api/endpoints/rainfall_climatology.py
import logging
from fastapi import APIRouter, Depends, Request, HTTPException
import ee

from app.core.limiter import limiter
from app.api.deps import get_current_user, get_geometry
from app.services.gee.rainfall_climatology import (
    get_monthly_climatology,
    get_annual_climatology
)
from app.services.cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
    CACHE_90_DAYS
)

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/rainfall/climatology",
    tags=["Rainfall Climatology"]
)

@router.post("/monthly")
@limiter.limit("15/minute")
def monthly_climatology(request: Request,
    geometry: ee.Geometry = Depends(get_geometry),
    user: dict = Depends(get_current_user)
):
    try:
        payload = {
            "geometry": geometry.getInfo()
        }
        cache_key = build_cache_key("monthly_climatology", payload)
        cached = get_cache(cache_key)
        if cached:
            logger.info(f"Cache HIT: monthly_climatology for {user.get('uid')}")
            return cached

        logger.info(f"Cache MISS: monthly_climatology for {user.get('uid')}")
        data = get_monthly_climatology(geometry)
        response = {
            "status": "success",
            "dataset": "CHIRPS",
            "units": "mm",
            **data
        }
        set_cache(cache_key, response, CACHE_90_DAYS)
        return response
    except Exception as e:
        logger.error("Monthly climatology endpoint failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")

@router.post("/annual")
@limiter.limit("15/minute")
def annual_climatology(request: Request,
    geometry: ee.Geometry = Depends(get_geometry),
    user: dict = Depends(get_current_user)
):
    try:
        payload = {
            "geometry": geometry.getInfo()
        }
        cache_key = build_cache_key("annual_climatology", payload)
        cached = get_cache(cache_key)
        if cached:
            logger.info(f"Cache HIT: annual_climatology for {user.get('uid')}")
            return cached

        logger.info(f"Cache MISS: annual_climatology for {user.get('uid')}")
        data = get_annual_climatology(geometry)
        response = {
            "status": "success",
            "dataset": "CHIRPS",
            "units": "mm",
            **data
        }
        set_cache(cache_key, response, CACHE_90_DAYS)
        return response
    except Exception as e:
        logger.error("Annual climatology endpoint failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
