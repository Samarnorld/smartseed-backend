from fastapi import APIRouter, Depends, Query
import ee

from app.api.deps import get_geometry
from app.services.gee.ndvi import get_ndvi_summary

router = APIRouter(
    prefix="/ndvi",
    tags=["NDVI"]
)


@router.post("/summary")
def ndvi_summary(
    geometry: ee.Geometry = Depends(get_geometry),
    start_date: str = Query(..., example="2024-01-01"),
    end_date: str = Query(..., example="2024-01-31")
):
    """
    Mean NDVI over a geometry for a given time range.
    """

    data = get_ndvi_summary(
        geometry=geometry,
        start_date=start_date,
        end_date=end_date
    )

    return {
        "status": "success",
        "ndvi": data
    }