import logging
from fastapi import APIRouter, Depends, Request, HTTPException
import ee

from app.core.limiter import limiter
from app.api.deps import get_current_user, get_geometry
from app.services.gee.elevation_tiles import get_elevation_tiles

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/elevation",
    tags=["Elevation & Terrain"]
)

@router.post("/tiles")
@limiter.limit("20/minute")
def elevation_tiles(request: Request,
    geometry: ee.Geometry = Depends(get_geometry),
    user: dict = Depends(get_current_user)
):
    try:
        tiles = get_elevation_tiles(geometry)
        logger.info(f"Elevation tiles requested by {user.get('uid')}")
        return {
            "status": "success",
            "dataset": "SRTM 30m",
            "units": "meters",
            **tiles
        }
    except Exception as e:
        logger.error("Elevation tiles failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate elevation tiles")
