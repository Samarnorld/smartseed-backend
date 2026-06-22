# app/api/endpoints/maize_suitability.py
import logging
from fastapi import APIRouter, Request, Depends, HTTPException
import ee
from app.core.limiter import limiter
from app.api.deps import get_current_user
from app.api.schemas import MaizeSuitabilityRequest
from app.services.gee.geometry import geojson_to_ee
from app.services.gee.maize_suitability import compute_maize_suitability

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Maize Suitability"])

@router.post("/maize/suitability")
@limiter.limit("20/minute")
def maize_suitability(request: Request,
    req: MaizeSuitabilityRequest,
    user: dict = Depends(get_current_user)
):
    """Analyze maize suitability. Requires authentication."""
    try:
        ee_geometry = geojson_to_ee(req.geometry)
        logger.info(f"Maize suitability requested by {user.get('uid')} for year {req.year}")

        return compute_maize_suitability(
            geometry=ee_geometry,
            year=req.year,
            season=req.season.value,
            depth="0-20cm"
        )
    except Exception as e:
        logger.error(f"Maize suitability analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
