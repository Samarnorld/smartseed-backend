# services/gee/rainfall_monthly.py
import ee

CHIRPS = "UCSB-CHG/CHIRPS/DAILY"
from datetime import datetime

def get_monthly_rainfall(
    geometry: ee.Geometry,
    year: int
):

    today = datetime.utcnow()
    current_year = today.year

    # Prevent future year
    if year > current_year:
        return []

    year_end = f"{year}-12-31"

    # Partial current year
    if year == current_year:
        year_end = today.strftime("%Y-%m-%d")

    collection = (
        ee.ImageCollection(CHIRPS)
        .filterBounds(geometry)
        .filterDate(f"{year}-01-01", year_end)
        .select("precipitation")
    )

    results = []

    for month in range(1, 13):

        # Skip future months in current year
        if year == current_year and month > today.month:
            results.append({
                "month": month,
                "total_mm": None
            })
            continue

        start = ee.Date.fromYMD(year, month, 1)
        end = start.advance(1, "month")

        monthly = collection.filterDate(start, end)
        image_count = monthly.size().getInfo()

        if image_count == 0:
            results.append({
                "month": month,
                "total_mm": None
            })
            continue

        total_img = monthly.sum()

        stats = total_img.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=5000,
            bestEffort=True
        )

        total_mm = stats.get("precipitation").getInfo()

        results.append({
            "month": month,
            "total_mm": total_mm
        })

    return results