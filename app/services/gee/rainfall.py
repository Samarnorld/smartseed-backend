# services/gee/rainfall.py
import ee
from datetime import datetime

CHIRPS_ID = "UCSB-CHG/CHIRPS/DAILY"

# Custom Date Range Rainfall
def compute_rainfall(
    geometry: ee.Geometry,
    start_date: str,
    end_date: str
) -> dict:
    """
    Compute rainfall statistics using CHIRPS DAILY.
    Returns total and mean rainfall (mm).
    """

    # Validate date format
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)
    today = datetime.utcnow()

    # Prevent future date ranges
    if start_dt > today or end_dt > today:
        return {
            "total_mm": None,
            "days": 0,
            "mean_mm_per_day": None,
            "message": "Future date range not allowed."
        }

    collection = (
        ee.ImageCollection(CHIRPS_ID)
        .filterDate(start_date, end_date)
        .filterBounds(geometry)
    )

    image_count = collection.size()
    image_count_val = image_count.getInfo()

    # Prevent division by zero
    if image_count_val == 0:
        return {
            "total_mm": None,
            "days": 0,
            "mean_mm_per_day": None
        }

    total_rainfall = collection.sum()

    stats = total_rainfall.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=5566,
        maxPixels=1e13
    )

    total_mm = ee.Number(stats.get("precipitation"))

    result = ee.Dictionary({
        "total_mm": total_mm,
        "days": image_count,
        "mean_mm_per_day": total_mm.divide(image_count)
    })

    return result.getInfo()

# Annual Rainfall (Single Year)
def get_annual_rainfall(
    geometry: ee.Geometry,
    year: int
):

    today = datetime.utcnow()
    current_year = today.year

    if year < 1981:
        raise ValueError("CHIRPS data starts from 1981.")

    # Prevent future year
    if year > current_year:
        return {
            "year": year,
            "total_mm": None,
            "message": "Year is in the future."
        }

    year_end = f"{year}-12-31"

    # Partial current year
    if year == current_year:
        year_end = today.strftime("%Y-%m-%d")

    collection = (
        ee.ImageCollection(CHIRPS_ID)
        .filterBounds(geometry)
        .filterDate(f"{year}-01-01", year_end)
    )

    image_count = collection.size().getInfo()

    if image_count == 0:
        return {
            "year": year,
            "total_mm": None
        }

    total_img = collection.sum()

    stats = total_img.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=5566,
        maxPixels=1e13
    )

    total_mm = ee.Number(stats.get("precipitation")).getInfo()

    return {
        "year": year,
        "total_mm": total_mm
    }