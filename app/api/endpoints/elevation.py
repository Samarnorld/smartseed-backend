import logging
from fastapi import APIRouter, Depends, Request, HTTPException
import ee

from app.core.limiter import limiter
from app.api.deps import get_current_user
from app.services.gee.geometry import geojson_to_ee
from app.services.gee.elevation import get_elevation_and_slope

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/elevation",
    tags=["Elevation & Terrain"]
)

@router.post("/summary")
@limiter.limit("20/minute")
def elevation_summary(request: Request,
    geometry: dict,
    user: dict = Depends(get_current_user)
):
    """Get elevation and slope data. Requires authentication."""
    try:
        ee_geometry = geojson_to_ee(geometry)
        logger.info(f"Elevation summary requested by {user.get('uid')}")
        data = get_elevation_and_slope(ee_geometry)

        return {
            "status": "success",
            "dataset": "SRTM 30m",
            **data
        }
    except Exception as e:
        logger.error(f"Elevation analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
