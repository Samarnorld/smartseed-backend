# app/api/endpoints/rainfall_anomaly.py
import logging
from fastapi import APIRouter, Depends, Query, Request, HTTPException
import ee
from app.core.limiter import limiter
from app.api.deps import get_current_user, get_geometry
from app.api.schemas import SeasonEnum
from app.services.gee.geometry import geojson_to_ee
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

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rainfall", tags=["Rainfall Anomaly"])

@router.post("/anomaly/seasonal")
@limiter.limit("20/minute")
def seasonal_anomaly(request: Request,
    geometry: dict,
    year: int = Query(..., ge=1981, le=2100),
    season: SeasonEnum = Query(...),
    user: dict = Depends(get_current_user)
):
    """Get seasonal rainfall anomaly. Requires authentication."""
    try:
        ee_geometry = geojson_to_ee(geometry)
        payload = {
            "geometry": ee_geometry.getInfo(),
            "year": year,
            "season": season.value
        }
        cache_key = build_cache_key("seasonal_anomaly", payload)
        
        if cache_key:
            cached = get_cache(cache_key)
            if cached:
                logger.info(f"Cache HIT: seasonal_anomaly for {user.get('uid')}")
                return cached
        
        logger.info(f"Seasonal anomaly requested by {user.get('uid')} for year {year}")
        result = get_seasonal_anomaly(ee_geometry, year, season.value)
        response = {"dataset": "CHIRPS", "units": "mm", **result}
        
        if cache_key:
            set_cache(cache_key, response, CACHE_30_DAYS)
        return response
    except Exception as e:
        logger.error(f"Seasonal anomaly failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")

@router.post("/anomaly/annual")
@limiter.limit("20/minute")
def annual_anomaly(request: Request,
    geometry: dict,
    year: int = Query(..., ge=1981, le=2100),
    user: dict = Depends(get_current_user)
):
    """Get annual rainfall anomaly. Requires authentication."""
    try:
        ee_geometry = geojson_to_ee(geometry)
        payload = {"geometry": ee_geometry.getInfo(), "year": year}
        cache_key = build_cache_key("annual_anomaly", payload)
        
        if cache_key:
            cached = get_cache(cache_key)
            if cached:
                logger.info(f"Cache HIT: annual_anomaly for {user.get('uid')}")
                return cached
        
        logger.info(f"Annual anomaly requested by {user.get('uid')} for year {year}")
        result = get_annual_anomaly(ee_geometry, year)
        response = {"dataset": "CHIRPS", "units": "mm", **result}
        
        if cache_key:
            set_cache(cache_key, response, CACHE_30_DAYS)
        return response
    except Exception as e:
        logger.error(f"Annual anomaly failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")

@router.post("/anomaly/monthly")
@limiter.limit("20/minute")
def monthly_anomaly(request: Request,
    geometry: dict,
    year: int = Query(..., ge=1981, le=2100),
    month: int = Query(..., ge=1, le=12),
    user: dict = Depends(get_current_user)
):
    """Get monthly rainfall anomaly. Requires authentication."""
    try:
        ee_geometry = geojson_to_ee(geometry)
        payload = {"geometry": ee_geometry.getInfo(), "year": year, "month": month}
        cache_key = build_cache_key("monthly_anomaly", payload)
        
        if cache_key:
            cached = get_cache(cache_key)
            if cached:
                logger.info(f"Cache HIT: monthly_anomaly for {user.get('uid')}")
                return cached
        
        logger.info(f"Monthly anomaly requested by {user.get('uid')} for {year}-{month}")
        result = get_monthly_anomaly(ee_geometry, year, month)
        response = {"dataset": "CHIRPS", "units": "mm", **result}
        
        if cache_key:
            set_cache(cache_key, response, CACHE_30_DAYS)
        return response
    except Exception as e:
        logger.error(f"Monthly anomaly failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
