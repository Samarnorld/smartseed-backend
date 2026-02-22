# app/services/gee/soil_raw.py
import ee
from app.services.gee.soil_config import (
    ISDA_BASE,
    SOIL_LAYERS,
    VALID_DEPTHS,
    SOIL_SCALING,
)

def get_raw_soil_data(geometry: ee.Geometry, depth: str):

    if depth not in VALID_DEPTHS:
        return {"status": "error", "message": "Invalid depth"}

    band_name = VALID_DEPTHS[depth]

    try:
        results = {}

        for key, dataset in SOIL_LAYERS.items():

            image = ee.Image(f"{ISDA_BASE}/{dataset}")
            band = image.select(band_name)

            stats = band.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=250,
                maxPixels=1e13,
            )

            stats_dict = stats.getInfo()

            if stats_dict:
                value = list(stats_dict.values())[0]
            else:
                value = None

            # Apply scaling
            scale = SOIL_SCALING.get(key, 1)
            if value is not None:
                value = value * scale

            results[key] = {
                "mean": value
            }

        return {
            "status": "success",
            "depth": depth,
            "soil_profile": results,
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}