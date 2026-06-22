import logging
from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from typing import List
import ee

from app.core.limiter import limiter
from app.api.deps import get_current_user
from app.services.gee.geometry import geojson_to_ee
from app.services.gee.soil_tiles import get_multi_soil_tiles

logger = logging.getLogger(__name__)
router = APIRouter()

class SoilTilesRequest(BaseModel):
    geometry: dict
    datasets: List[str]
    depth: str = "0-20cm"


@router.post("/soil/tiles")
@limiter.limit("20/minute")
def soil_tiles(request: Request,
    payload: SoilTilesRequest,
    user: dict = Depends(get_current_user)
):
    try:
        logger.info(f"Soil tiles request by {user.get('uid')} datasets={payload.datasets}")
        ee_geometry = geojson_to_ee(payload.geometry)
        tiles = get_multi_soil_tiles(
            ee_geometry,
            payload.datasets,
            payload.depth
        )
        return {
            "status": "success",
            **tiles
        }
    except Exception as e:
        logger.error("Soil tiles generation failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate soil tiles")
