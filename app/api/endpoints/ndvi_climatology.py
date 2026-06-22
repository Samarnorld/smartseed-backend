# app/api/endpoints/ndvi_climatology.py
import logging
from fastapi import APIRouter, Depends, Request, HTTPException
import ee
from app.core.limiter import limiter
from app.api.deps import get_current_user
from app.services.gee.geometry import geojson_to_ee
from app.services.gee.ndvi_climatology import get_ndvi_climatology

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ndvi", tags=["NDVI"])

@router.post("/climatology")
@limiter.limit("20/minute")
def ndvi_climatology(request: Request,
    geometry: dict,
    user: dict = Depends(get_current_user)
):
    """Get NDVI climatology. Requires authentication."""
    try:
        ee_geometry = geojson_to_ee(geometry)
        logger.info(f"NDVI climatology requested by {user.get('uid')}")
        return get_ndvi_climatology(ee_geometry)
    except Exception as e:
        logger.error(f"NDVI climatology failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
