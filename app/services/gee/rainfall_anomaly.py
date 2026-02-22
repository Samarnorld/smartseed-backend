# app/services/gee/rainfall_anomaly.py
import ee
from datetime import datetime
import calendar

CHIRPS_ID = "UCSB-CHG/CHIRPS/DAILY"

SEASONS = {
    "long_rains": ("03-01", "05-31"),   # MAM
    "short_rains": ("10-01", "12-31")   # OND
}

# Helper Functions
def _rolling_baseline_years():
    today = datetime.utcnow()
    end_year = today.year - 1
    start_year = end_year - 19
    return start_year, end_year

def _compute_anomaly(current_val, baseline_val):
    if not baseline_val or baseline_val == 0:
        return None, "No baseline data"

    anomaly_percent = ((current_val - baseline_val) / baseline_val) * 100

    if anomaly_percent < -10:
        interpretation = "Below normal"
    elif anomaly_percent > 10:
        interpretation = "Above normal"
    else:
        interpretation = "Near normal"

    return anomaly_percent, interpretation


def _reduce_to_mean(image, geometry):
    return (
        image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=5566,
            maxPixels=1e13
        )
        .get("precipitation")
    )

# SEASONAL ANOMALY
def get_seasonal_anomaly(geometry: ee.Geometry, year: int, season: str):

    if season not in SEASONS:
        raise ValueError("Invalid season. Use 'long_rains' or 'short_rains'.")

    today = datetime.utcnow()
    current_year = today.year

    if year > current_year:
        raise ValueError("Year cannot be in the future.")

    start_mm, end_mm = SEASONS[season]
    season_start = f"{year}-{start_mm}"
    season_end = f"{year}-{end_mm}"

    season_start_dt = datetime.fromisoformat(season_start)
    season_end_dt = datetime.fromisoformat(season_end)

    # If season not started yet
    if year == current_year and today < season_start_dt:
        return {
            "status": "not_started",
            "type": "seasonal",
            "season": season,
            "year": year,
            "message": f"{season} {year} has not started yet."
        }

    # Partial current season
    if year == current_year and today < season_end_dt:
        season_end = today.strftime("%Y-%m-%d")

    chirps = ee.ImageCollection(CHIRPS_ID).filterBounds(geometry)

    current_img = chirps.filterDate(season_start, season_end).sum()
    current_val = ee.Number(_reduce_to_mean(current_img, geometry)).getInfo()

    baseline_start_year, baseline_end_year = _rolling_baseline_years()

    baseline_collection = ee.ImageCollection([
        chirps.filterDate(f"{y}-{start_mm}", f"{y}-{end_mm}").sum()
        for y in range(baseline_start_year, baseline_end_year + 1)
    ])

    baseline_img = baseline_collection.mean()
    baseline_val = ee.Number(_reduce_to_mean(baseline_img, geometry)).getInfo()

    anomaly_percent, interpretation = _compute_anomaly(current_val, baseline_val)

    return {
        "status": "success",
        "type": "seasonal",
        "season": season,
        "year": year,
        "total_mm": current_val,
        "long_term_mean_mm": baseline_val,
        "anomaly_percent": anomaly_percent,
        "interpretation": interpretation,
        "baseline_period": f"{baseline_start_year}-{baseline_end_year}"
    }

# ANNUAL ANOMALY
def get_annual_anomaly(geometry: ee.Geometry, year: int):

    today = datetime.utcnow()
    current_year = today.year

    if year > current_year:
        raise ValueError("Year cannot be in the future.")

    year_start = f"{year}-01-01"
    year_end = f"{year}-12-31"

    if year == current_year:
        year_end = today.strftime("%Y-%m-%d")

    chirps = ee.ImageCollection(CHIRPS_ID).filterBounds(geometry)

    current_img = chirps.filterDate(year_start, year_end).sum()
    current_val = ee.Number(_reduce_to_mean(current_img, geometry)).getInfo()

    baseline_start_year, baseline_end_year = _rolling_baseline_years()

    baseline_collection = ee.ImageCollection([
        chirps.filterDate(f"{y}-01-01", f"{y}-12-31").sum()
        for y in range(baseline_start_year, baseline_end_year + 1)
    ])

    baseline_img = baseline_collection.mean()
    baseline_val = ee.Number(_reduce_to_mean(baseline_img, geometry)).getInfo()

    anomaly_percent, interpretation = _compute_anomaly(current_val, baseline_val)

    return {
        "status": "success",
        "type": "annual",
        "year": year,
        "total_mm": current_val,
        "long_term_mean_mm": baseline_val,
        "anomaly_percent": anomaly_percent,
        "interpretation": interpretation,
        "baseline_period": f"{baseline_start_year}-{baseline_end_year}"
    }

# MONTHLY ANOMALY
def get_monthly_anomaly(geometry: ee.Geometry, year: int, month: int):

    today = datetime.utcnow()
    current_year = today.year

    if year > current_year:
        raise ValueError("Year cannot be in the future.")

    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12.")

    month_start = f"{year}-{month:02d}-01"
    last_day = calendar.monthrange(year, month)[1]
    month_end = f"{year}-{month:02d}-{last_day}"

    # Month not started yet
    if year == current_year and month > today.month:
        return {
            "status": "not_started",
            "type": "monthly",
            "year": year,
            "month": month,
            "message": f"Month {month} {year} has not started yet."
        }

    # Partial current month
    if year == current_year and month == today.month:
        month_end = today.strftime("%Y-%m-%d")

    chirps = ee.ImageCollection(CHIRPS_ID).filterBounds(geometry)

    current_img = chirps.filterDate(month_start, month_end).sum()
    current_val = ee.Number(_reduce_to_mean(current_img, geometry)).getInfo()

    baseline_start_year, baseline_end_year = _rolling_baseline_years()

    baseline_collection = ee.ImageCollection([
        chirps.filterDate(f"{y}-{month:02d}-01",
                          f"{y}-{month:02d}-{calendar.monthrange(y, month)[1]}").sum()
        for y in range(baseline_start_year, baseline_end_year + 1)
    ])

    baseline_img = baseline_collection.mean()
    baseline_val = ee.Number(_reduce_to_mean(baseline_img, geometry)).getInfo()

    anomaly_percent, interpretation = _compute_anomaly(current_val, baseline_val)

    return {
        "status": "success",
        "type": "monthly",
        "year": year,
        "month": month,
        "total_mm": current_val,
        "long_term_mean_mm": baseline_val,
        "anomaly_percent": anomaly_percent,
        "interpretation": interpretation,
        "baseline_period": f"{baseline_start_year}-{baseline_end_year}"
    }