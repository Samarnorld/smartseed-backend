# app/api/endpoints/maize_timeseries.py
import logging
from fastapi import APIRouter, Request, Depends, HTTPException
import ee
from app.core.limiter import limiter
from app.api.deps import get_current_user
from app.api.schemas import MaizeTimeseriesRequest
from app.services.gee.geometry import geojson_to_ee
from app.services.gee.maize_timeseries import maize_time_series

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Maize Time Series"])

@router.post("/maize/timeseries")
@limiter.limit("20/minute")
def maize_timeseries(request: Request,
    req: MaizeTimeseriesRequest,
    user: dict = Depends(get_current_user)
):
    """Analyze maize timeseries. Requires authentication."""
    try:
        ee_geometry = geojson_to_ee(req.geometry)
        logger.info(f"Maize timeseries requested by {user.get('uid')} for years {req.start_year}-{req.end_year}")

        return maize_time_series(
            geometry=ee_geometry,
            start_year=req.start_year,
            end_year=req.end_year,
            season=req.season.value
        )
    except Exception as e:
        logger.error(f"Maize timeseries analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
