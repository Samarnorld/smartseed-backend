# app/services/gee/rainfall_climatology.py
import ee
from datetime import datetime
import calendar

CHIRPS = "UCSB-CHG/CHIRPS/DAILY"

# Rolling 20-Year Baseline
def _rolling_baseline():
    """
    Returns rolling 20-year baseline period.
    Example (if current year is 2026):
    2006–2025
    """
    current_year = datetime.utcnow().year
    end_year = current_year - 1
    start_year = end_year - 19
    return start_year, end_year

def _reduce_mean(image, geometry):
    return image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=5566,
        maxPixels=1e13
    ).get("precipitation")

# Monthly Climatology
def get_monthly_climatology(geometry: ee.Geometry):

    start_year, end_year = _rolling_baseline()

    chirps = ee.ImageCollection(CHIRPS).filterBounds(geometry)

    monthly_results = []

    for month in range(1, 13):

        monthly_images = []

        for year in range(start_year, end_year + 1):

            start_date = f"{year}-{month:02d}-01"
            last_day = calendar.monthrange(year, month)[1]
            end_date = f"{year}-{month:02d}-{last_day}"

            monthly_images.append(
                chirps.filterDate(start_date, end_date).sum()
            )

        monthly_mean = ee.ImageCollection(monthly_images).mean()

        value = ee.Number(
            _reduce_mean(monthly_mean, geometry)
        ).getInfo()

        monthly_results.append({
            "month": month,
            "historical_mean_mm": value
        })

    return {
        "baseline_period": f"{start_year}-{end_year}",
        "monthly_climatology": monthly_results
    }

# Annual Climatology
def get_annual_climatology(geometry: ee.Geometry):

    start_year, end_year = _rolling_baseline()

    chirps = ee.ImageCollection(CHIRPS).filterBounds(geometry)

    annual_images = []

    for year in range(start_year, end_year + 1):
        annual_images.append(
            chirps
            .filterDate(f"{year}-01-01", f"{year}-12-31")
            .sum()
        )

    annual_mean = ee.ImageCollection(annual_images).mean()

    value = ee.Number(
        _reduce_mean(annual_mean, geometry)
    ).getInfo()

    return {
        "baseline_period": f"{start_year}-{end_year}",
        "historical_mean_annual_mm": value
    }