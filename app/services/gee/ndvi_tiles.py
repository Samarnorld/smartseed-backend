# app/services/gee/ndvi_tiles.py
import ee
from datetime import datetime

S2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"

def _add_ndvi(image: ee.Image) -> ee.Image:
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    return image.addBands(ndvi)

def get_ndvi_tiles(geometry, start_date, end_date):

    today = datetime.utcnow().strftime("%Y-%m-%d")
    if end_date > today:
        raise ValueError("Future date not allowed")

    collection = (
        ee.ImageCollection(S2_COLLECTION)
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .map(_add_ndvi)
    )

    if collection.size().getInfo() == 0:
        raise ValueError("No Sentinel-2 images found for this period.")

    mean_ndvi = collection.select("NDVI").mean().clip(geometry)

    vis_params = {
        "min": 0.0,
        "max": 0.8,
        "palette": ["brown", "yellow", "green"]
    }

    map_id = mean_ndvi.getMapId(vis_params)

    return {
        "tile_url": map_id["tile_fetcher"].url_format,
        "dataset": "Sentinel-2 SR",
        "index": "NDVI",
        "date_range": {
            "start": start_date,
            "end": end_date
        }
    }