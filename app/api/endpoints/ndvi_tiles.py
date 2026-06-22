import logging
from fastapi import APIRouter, Depends, Query, Request, HTTPException
import ee

from app.core.limiter import limiter
from app.api.deps import get_current_user, get_geometry
from app.services.gee.ndvi_tiles import get_ndvi_tiles

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ndvi", tags=["NDVI"])

@router.post("/tiles")
@limiter.limit("10/minute")
def ndvi_tiles(request: Request,
    geometry: ee.Geometry = Depends(get_geometry),
    start_date: str = Query(...),
    end_date: str = Query(...),
    user: dict = Depends(get_current_user)
):
    """
    Returns tile URL for NDVI visualization.
    """

    try:
        data = get_ndvi_tiles(
            geometry=geometry,
            start_date=start_date,
            end_date=end_date
        )

        logger.info(f"NDVI tiles requested by {user.get('uid')}")
        return {
            "status": "success",
            "tiles": data
        }

    except Exception as e:
        logger.error("NDVI tiles generation failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate NDVI tiles")
