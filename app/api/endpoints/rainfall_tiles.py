# app/api/endpoints/rainfall_tiles.py
from fastapi import APIRouter, Depends, Query
import ee

from app.api.deps import get_geometry
from app.services.gee.rainfall_tiles import get_rainfall_tiles

router = APIRouter(
    prefix="/rainfall/tiles",
    tags=["Rainfall Raster"]
)

@router.post("")
def rainfall_tiles(
    geometry: ee.Geometry = Depends(get_geometry),
    start_date: str = Query(...),
    end_date: str = Query(...)
):

    tiles = get_rainfall_tiles(
        geometry=geometry,
        start_date=start_date,
        end_date=end_date
    )

    return {
        "status": "success",
        "dataset": "CHIRPS",
        "units": "mm",
        **tiles
    }
