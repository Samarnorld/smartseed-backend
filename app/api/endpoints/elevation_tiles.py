from fastapi import APIRouter, Depends
import ee

from app.api.deps import get_geometry
from app.services.gee.elevation_tiles import get_elevation_tiles

router = APIRouter(
    prefix="/elevation",
    tags=["Elevation & Terrain"]
)

@router.post("/tiles")
def elevation_tiles(
    geometry: ee.Geometry = Depends(get_geometry)
):
    tiles = get_elevation_tiles(geometry)

    return {
        "status": "success",
        "dataset": "SRTM 30m",
        "units": "meters",
        **tiles
    }
