# app/services/gee/temperature_monthly.py
import ee
from datetime import datetime

ERA5_DAILY = "ECMWF/ERA5_LAND/DAILY_AGGR"

def get_monthly_temperature(geometry: ee.Geometry, year: int):

    now = datetime.utcnow()
    current_year = now.year
    current_month = now.month

    collection = (
        ee.ImageCollection(ERA5_DAILY)
        .filterBounds(geometry)
        .filterDate(f"{year}-01-01", f"{year}-12-31")
        .select("temperature_2m")
    )

    results = []

    for month in range(1, 13):

        if year > current_year:
            results.append({"month": month, "mean_c": None})
            continue

        if year == current_year and month > current_month:
            results.append({"month": month, "mean_c": None})
            continue

        start = ee.Date.fromYMD(year, month, 1)
        end = start.advance(1, "month")

        monthly = collection.filterDate(start, end)

        if monthly.size().getInfo() == 0:
            results.append({"month": month, "mean_c": None})
            continue

        mean_img = monthly.mean()

        stats = mean_img.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=1000,
            bestEffort=True,
            maxPixels=1e9
        )

        mean_k = stats.get("temperature_2m")

        if mean_k is None:
            results.append({"month": month, "mean_c": None})
            continue

        results.append({
            "month": month,
            "mean_c": ee.Number(mean_k).subtract(273.15).getInfo()
        })

    return results