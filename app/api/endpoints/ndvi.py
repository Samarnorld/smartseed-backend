# app/api/endpoints/ndvi.py
import logging
from fastapi import APIRouter, Depends, Request, HTTPException
import ee

from app.core.limiter import limiter
from app.api.deps import get_current_user
from app.api.schemas import NDVIAnalysisRequest
from app.services.gee.geometry import geojson_to_ee
from app.services.gee.ndvi import get_ndvi_summary, get_ndvi_timeseries

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ndvi", tags=["NDVI"])

@router.post("/summary")
@limiter.limit("20/minute")
def ndvi_summary(request: Request,
    req: NDVIAnalysisRequest,
    user: dict = Depends(get_current_user)
):
    """Get NDVI summary for a geometry. Requires authentication."""
    try:
        geometry = geojson_to_ee(req.geometry)
        logger.info(f"NDVI summary requested by {user.get('uid')} for years {req.start_year}-{req.end_year}")
        return get_ndvi_summary(geometry, req.start_year, req.end_year)
    except Exception as e:
        logger.error(f"NDVI summary failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")

@router.post("/timeseries")
@limiter.limit("20/minute")
def ndvi_timeseries(request: Request,
    req: NDVIAnalysisRequest,
    user: dict = Depends(get_current_user)
):
    """Get NDVI time series for a geometry. Requires authentication."""
    try:
        geometry = geojson_to_ee(req.geometry)
        logger.info(f"NDVI timeseries requested by {user.get('uid')} for years {req.start_year}-{req.end_year}")
        return get_ndvi_timeseries(geometry, req.start_year, req.end_year)
    except Exception as e:
        logger.error(f"NDVI timeseries failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
