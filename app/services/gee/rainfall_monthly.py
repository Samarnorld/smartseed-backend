# services/gee/rainfall_monthly.py
import ee
from datetime import datetime
CHIRPS = "UCSB-CHG/CHIRPS/DAILY"

def get_monthly_rainfall(
    geometry: ee.Geometry,
    year: int
):
    today = datetime.utcnow()
    current_year = today.year
    if year > current_year:
        return []
    year_end = f"{year}-12-31"
    if year == current_year:
        year_end = today.strftime("%Y-%m-%d")
    collection = (
        ee.ImageCollection(CHIRPS)
        .filterBounds(geometry)
        .filterDate(f"{year}-01-01", year_end)
        .select("precipitation")
    )

    # Adding month property to each image
    def add_month(img):
        return img.set("month", img.date().get("month"))
    collection = collection.map(add_month)
    months = ee.List.sequence(1, 12)
    def monthly_sum(m):
        m = ee.Number(m)
        monthly = collection.filter(
            ee.Filter.eq("month", m)
        )
        total_img = monthly.sum()
        stats = total_img.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=5566,
            maxPixels=1e13,
            bestEffort=True
        )
        precip = stats.get("precipitation")
        safe_precip = ee.Algorithms.If(
            precip,
            precip,
            0
        )
        return ee.Dictionary({
            "month": m,
            "total_mm": safe_precip
        })
    results = months.map(monthly_sum)
    return ee.List(results).getInfo()