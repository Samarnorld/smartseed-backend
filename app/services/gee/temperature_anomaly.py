# app/services/gee/temperature_anomaly.py
import ee
from datetime import datetime

ERA5_DAILY = "ECMWF/ERA5_LAND/DAILY_AGGR"

SEASONS = {
    "MAM": [3, 4, 5],
    "JJA": [6, 7, 8],
    "SON": [9, 10, 11],
    "DJF": [12, 1, 2]
}

def _season_collection(year: int, season: str, geometry) -> ee.ImageCollection:
    months = SEASONS[season]
    collection = ee.ImageCollection([])

    for m in months:
        if season == "DJF" and m in [1, 2]:
            y = year + 1
        else:
            y = year

        start = ee.Date.fromYMD(y, m, 1)
        end = start.advance(1, "month")

        col = (
            ee.ImageCollection(ERA5_DAILY)
            .filterBounds(geometry)
            .filterDate(start, end)
            .select(["temperature_2m", "temperature_2m_max"])
        )

        collection = collection.merge(col)

    return collection

# SECTION A
def get_current_season_overview(geometry, season, year):

    now = datetime.utcnow()
    current_year = now.year

    if year > current_year:
        return {
            "mean_temp_c": None,
            "hottest_day_c": None,
            "coldest_day_c": None,
            "heat_stress_days_above_35C": None
        }

    collection = _season_collection(year, season, geometry)

    if collection.size().getInfo() == 0:
        return {
            "mean_temp_c": None,
            "hottest_day_c": None,
            "coldest_day_c": None,
            "heat_stress_days_above_35C": None
        }

    mean_img = collection.select("temperature_2m").mean()
    max_img = collection.select("temperature_2m_max").max()
    min_img = collection.select("temperature_2m").min()

    heat_threshold = 308.15

    hot_days = collection.filter(
        ee.Filter.gt("temperature_2m_max", heat_threshold)
    )

    mean_stats = mean_img.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=1000,
        bestEffort=True,
        maxPixels=1e9
    )

    mean_k = mean_stats.get("temperature_2m")

    if mean_k is None:
        return {
            "mean_temp_c": None,
            "hottest_day_c": None,
            "coldest_day_c": None,
            "heat_stress_days_above_35C": None
        }

    max_stats = max_img.reduceRegion(
        reducer=ee.Reducer.max(),
        geometry=geometry,
        scale=1000,
        bestEffort=True,
        maxPixels=1e9
    )

    min_stats = min_img.reduceRegion(
        reducer=ee.Reducer.min(),
        geometry=geometry,
        scale=1000,
        bestEffort=True,
        maxPixels=1e9
    )

    return {
        "mean_temp_c": ee.Number(mean_k).subtract(273.15).getInfo(),
        "hottest_day_c": ee.Number(max_stats.get("temperature_2m_max")).subtract(273.15).getInfo(),
        "coldest_day_c": ee.Number(min_stats.get("temperature_2m")).subtract(273.15).getInfo(),
        "heat_stress_days_above_35C": hot_days.size().getInfo()
    }

# SECTION B
def get_temperature_seasonal_anomaly(geometry, season, year):

    now = datetime.utcnow()
    current_year = now.year

    if year > current_year:
        return {
            "mean_temp_c": None,
            "climatology_mean_c": None,
            "anomaly_c": None,
            "indicator": None
        }

    target = _season_collection(year, season, geometry).mean()

    climatology = ee.ImageCollection([])

    for y in range(1991, 2021):
        climatology = climatology.merge(
            _season_collection(y, season, geometry)
        )

    climatology_mean = climatology.mean()

    target_stats = target.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=1000,
        bestEffort=True,
        maxPixels=1e9
    )

    clim_stats = climatology_mean.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=1000,
        bestEffort=True,
        maxPixels=1e9
    )

    if target_stats.get("temperature_2m") is None:
        return {
            "mean_temp_c": None,
            "climatology_mean_c": None,
            "anomaly_c": None,
            "indicator": None
        }

    target_c = ee.Number(target_stats.get("temperature_2m")).subtract(273.15)
    clim_c = ee.Number(clim_stats.get("temperature_2m")).subtract(273.15)

    anomaly = target_c.subtract(clim_c)

    indicator = ee.Algorithms.If(
        anomaly.gt(0),
        "Warmer than 30-year average",
        "Cooler than 30-year average"
    )

    return {
        "mean_temp_c": target_c.getInfo(),
        "climatology_mean_c": clim_c.getInfo(),
        "anomaly_c": anomaly.getInfo(),
        "indicator": indicator.getInfo()
    }

# SECTION C
def get_10yr_temperature_trend(geometry, season, year):

    now = datetime.utcnow()
    current_year = now.year

    if year >= current_year:
        end_year = current_year - 1
    else:
        end_year = year

    start_year = end_year - 9
    years = list(range(start_year, end_year + 1))

    data = []

    for y in years:
        seasonal = _season_collection(y, season, geometry).mean()

        stats = seasonal.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=1000,
            bestEffort=True,
            maxPixels=1e9
        )

        if stats.get("temperature_2m") is None:
            data.append({"year": y, "mean_temp_c": None})
            continue

        temp_c = ee.Number(stats.get("temperature_2m")).subtract(273.15)

        data.append({
            "year": y,
            "mean_temp_c": temp_c.getInfo()
        })

    valid = [d for d in data if d["mean_temp_c"] is not None]

    warming = False
    if len(valid) >= 2:
        warming = valid[-1]["mean_temp_c"] > valid[0]["mean_temp_c"]

    return {
        "trend_period_years": 10,
        "warming_detected": warming,
        "data": data
    }

def get_agronomic_interpretation(mean_temp_c, heat_days):

    if mean_temp_c is None:
        return {
            "temperature_suitability": "Data not yet available",
            "heat_stress_risk": "Data not yet available"
        }

    if mean_temp_c < 18:
        suitability = "Cool zone – Suitable for late-maturing highland hybrids"
    elif 18 <= mean_temp_c <= 26:
        suitability = "Optimal for most maize hybrids"
    else:
        suitability = "Warm zone – Consider early-maturing or drought-tolerant varieties"

    if heat_days is None:
        heat_risk = "Data not yet available"
    elif heat_days > 10:
        heat_risk = "High heat stress risk during flowering"
    elif heat_days > 3:
        heat_risk = "Moderate heat stress risk"
    else:
        heat_risk = "Low heat stress risk"

    return {
        "temperature_suitability": suitability,
        "heat_stress_risk": heat_risk
    }