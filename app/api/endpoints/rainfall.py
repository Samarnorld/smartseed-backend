# app/api/endpoints/rainfall.py
import logging
from fastapi import APIRouter, Depends, Request, HTTPException
import ee

from app.core.limiter import limiter
from app.api.deps import get_current_user
from app.api.schemas import RainfallAnalysisRequest, RainfallAnnualRequest
from app.services.gee.geometry import geojson_to_ee
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

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rainfall",
    tags=["Rainfall"]
)

# Custom Date Range
@router.post("/analyze")
@limiter.limit("20/minute")
def rainfall_analysis(request: Request,
    req: RainfallAnalysisRequest,
    user: dict = Depends(get_current_user)
):
    """Analyze rainfall for a custom date range. Requires authentication."""
    try:
        geometry = geojson_to_ee(req.geometry)
        start_date = str(req.start_date)
        end_date = str(req.end_date)
        
        payload = {
            "geometry": geometry.getInfo(),
            "start_date": start_date,
            "end_date": end_date
        }
        cache_key = build_cache_key("rainfall_analysis", payload)
        
        # Try cache
        if cache_key:
            cached = get_cache(cache_key)
            if cached:
                logger.info(f"Cache HIT: rainfall_analysis for {user.get('uid')}")
                return cached
        
        logger.info(f"Cache MISS: rainfall_analysis for {user.get('uid')}")
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
        
        # Store in cache
        if cache_key:
            set_cache(cache_key, result, CACHE_7_DAYS)
        
        return result
    except Exception as e:
        logger.error(f"Rainfall analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")

# Annual Rainfall
@router.post("/annual")
@limiter.limit("20/minute")
def annual_rainfall(request: Request,
    req: RainfallAnnualRequest,
    user: dict = Depends(get_current_user)
):
    """Get annual rainfall for a specific year. Requires authentication."""
    try:
        geometry = geojson_to_ee(req.geometry)
        
        payload = {
            "geometry": geometry.getInfo(),
            "year": req.year
        }
        cache_key = build_cache_key("annual_rainfall", payload)
        
        # Try cache
        if cache_key:
            cached = get_cache(cache_key)
            if cached:
                logger.info(f"Cache HIT: annual_rainfall for {user.get('uid')}")
                return cached
        
        logger.info(f"Cache MISS: annual_rainfall for {user.get('uid')}")
        result = get_annual_rainfall(
            geometry=geometry,
            year=req.year
        )
        
        response = {
            "status": "success",
            "dataset": "CHIRPS",
            "units": "mm",
            **result
        }
        
        # Store in cache
        if cache_key:
            set_cache(cache_key, response, CACHE_7_DAYS)
        
        return response
    except Exception as e:
        logger.error(f"Annual rainfall failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
