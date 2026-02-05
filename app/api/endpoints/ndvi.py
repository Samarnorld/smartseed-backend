from fastapi import APIRouter, Query
from services.gee.ndvi import get_mean_ndvi
import ee

router = APIRouter(prefix="/ndvi", tags=["NDVI"])


@router.post("/summary")
def ndvi_summary(
    geometry: dict,
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    """
    Mean NDVI over a geometry for a given time range.
    """

    try:
        ee_geometry = ee.Geometry(geometry)

        result = get_mean_ndvi(
            geometry=ee_geometry,
            start_date=start_date,
            end_date=end_date
        )

        return result

    except Exception as e:
        return {
            "error": "NDVI computation failed",
            "details": str(e)
        }