# app/api/endpoints/soil_analysis.py
import logging
from fastapi import APIRouter, Body, Request, Depends, HTTPException
import ee

from app.core.limiter import limiter
from app.api.deps import get_current_user
from app.api.schemas import SoilAnalysisRequest
from app.services.gee.soil_raw import get_raw_soil_data
from app.services.gee.soil_intelligence import build_soil_intelligence
from app.services.gee.geometry import geojson_to_ee
from app.services.cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
    CACHE_30_DAYS
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/soil/analysis")
@limiter.limit("20/minute")
def soil_analysis(request: Request,
    geometry: dict = Body(...),
    depth: str = "0-20cm",
    user: dict = Depends(get_current_user)
):
    """Analyze soil properties. Requires authentication."""
    try:
        # Validate depth
        allowed_depths = ["0-20cm", "20-50cm", "50-100cm"]
        if depth not in allowed_depths:
            raise ValueError(f"Depth must be one of: {', '.join(allowed_depths)}")
        
        payload = {
            "geometry": geometry,
            "depth": depth
        }
        cache_key = build_cache_key("soil_analysis", payload)
        
        # Try cache
        if cache_key:
            cached = get_cache(cache_key)
            if cached:
                logger.info(f"Cache HIT: soil_analysis for {user.get('uid')}")
                return cached
        
        logger.info(f"Cache MISS: soil_analysis for {user.get('uid')}")
        ee_geometry = geojson_to_ee(geometry)
        raw = get_raw_soil_data(ee_geometry, depth)
        
        if raw.get("status") != "success":
            logger.warning(f"Soil analysis failed: {raw}")
            return raw
        
        intelligence = build_soil_intelligence(raw["soil_profile"])
        result = {
            "status": "success",
            "depth": depth,
            "soil_intelligence": intelligence,
        }
        
        # Store in cache
        if cache_key:
            set_cache(cache_key, result, CACHE_30_DAYS)
        
        return result
    except ValueError as e:
        logger.warning(f"Invalid soil request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Soil analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
