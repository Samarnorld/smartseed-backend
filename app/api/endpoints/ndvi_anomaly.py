# app/api/endpoints/ndvi_anomaly.py
import logging
from fastapi import APIRouter, Depends, Query, Request, HTTPException
import ee
from app.core.limiter import limiter
from app.api.deps import get_current_user
from app.api.schemas import SeasonEnum
from app.services.gee.geometry import geojson_to_ee
from app.services.gee.ndvi_anomaly import get_seasonal_anomaly

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ndvi", tags=["NDVI"])

@router.post("/anomaly")
@limiter.limit("20/minute")
def ndvi_anomaly(request: Request,
    geometry: dict,
    year: int = Query(..., ge=2000, le=2100),
    season: SeasonEnum = Query(...),
    user: dict = Depends(get_current_user)
):
    """Get NDVI anomaly. Requires authentication."""
    try:
        ee_geometry = geojson_to_ee(geometry)
        logger.info(f"NDVI anomaly requested by {user.get('uid')} for year {year}")
        return get_seasonal_anomaly(ee_geometry, year, season.value)
    except Exception as e:
        logger.error(f"NDVI anomaly analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
