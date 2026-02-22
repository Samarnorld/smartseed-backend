from fastapi import APIRouter, Depends
import ee

from app.api.deps import get_geometry
from app.services.gee.elevation import get_elevation_and_slope

router = APIRouter(
    prefix="/elevation",
    tags=["Elevation & Terrain"]
)

@router.post("/summary")
def elevation_summary(
    geometry: ee.Geometry = Depends(get_geometry)
):
    data = get_elevation_and_slope(geometry)

    return {
        "status": "success",
        "dataset": "SRTM 30m",
        **data
    }
