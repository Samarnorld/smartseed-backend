# app/services/gee/ndvi_anomaly.py
import ee
from datetime import datetime

S2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"

SEASONS = {
    "MAM": [3, 4, 5],
    "JJA": [6, 7, 8],
    "SON": [9, 10, 11],
    "DJF": [12, 1, 2]
}

def _compute_ndvi(image):
    return image.normalizedDifference(["B8", "B4"]).rename("NDVI")

def _season_collection(geometry, year, season):

    months = SEASONS[season]
    collection = ee.ImageCollection([])

    for m in months:
        if m == 12:
            start = f"{year}-12-01"
            end = f"{year}-12-31"
        elif m in [1, 2]:
            start = f"{year+1}-{m:02d}-01"
            end = f"{year+1}-{m:02d}-28"
        else:
            start = f"{year}-{m:02d}-01"
            end = f"{year}-{m:02d}-28"

        col = (
            ee.ImageCollection(S2_COLLECTION)
            .filterBounds(geometry)
            .filterDate(start, end)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
            .map(_compute_ndvi)
        )

        collection = collection.merge(col)

    if collection.size().getInfo() == 0:
        return None

    return collection.mean().clip(geometry)

def get_seasonal_anomaly(geometry, year, season):

    if season not in SEASONS:
        raise ValueError("Invalid season")

    current_year = datetime.utcnow().year
    if year > current_year:
        raise ValueError("Future year not allowed")

    target_img = _season_collection(geometry, year, season)
    if target_img is None:
        return None

    target_val = target_img.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=10,
        bestEffort=True
    ).get("NDVI")

    target_val = ee.Number(target_val)

    # 5-year baseline
    baseline_images = []
    for y in range(year - 5, year):
        img = _season_collection(geometry, y, season)
        if img:
            baseline_images.append(img)

    if len(baseline_images) == 0:
        return None

    baseline = ee.ImageCollection(baseline_images).mean()

    baseline_val = baseline.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=10,
        bestEffort=True
    ).get("NDVI")

    baseline_val = ee.Number(baseline_val)

    # Prevent divide-by-zero
    anomaly = target_val.subtract(baseline_val)
    anomaly_percent = ee.Algorithms.If(
        baseline_val.eq(0),
        None,
        anomaly.divide(baseline_val).multiply(100)
    )

    return {
        "season": season,
        "year": year,
        "mean_ndvi": target_val.getInfo(),
        "baseline_ndvi": baseline_val.getInfo(),
        "anomaly_percent": ee.Number(anomaly_percent).getInfo()
        if anomaly_percent is not None else None
    }