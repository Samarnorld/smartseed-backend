from fastapi import APIRouter, Depends, Query
import ee

from app.api.deps import get_geometry
from app.services.gee.ndvi_tiles import get_ndvi_tiles

router = APIRouter(prefix="/ndvi", tags=["NDVI"])

@router.post("/tiles")
def ndvi_tiles(
    geometry: ee.Geometry = Depends(get_geometry),
    start_date: str = Query(...),
    end_date: str = Query(...)
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

        return {
            "status": "success",
            "tiles": data
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }