import ee
from app.services.gee.soil_config import (
    ISDA_BASE,
    SOIL_LAYERS,
    VALID_DEPTHS,
    SOIL_VIS,
    SOIL_SCALING,
)
def get_multi_soil_tiles(
    geometry: ee.Geometry,
    datasets: list,
    depth: str,
):
    if depth not in VALID_DEPTHS:
        return {"status": "error", "message": "Invalid depth"}
    band_name = VALID_DEPTHS[depth]
    tiles = {}
    for dataset in datasets:
        if dataset not in SOIL_LAYERS:
            continue  
        dataset_name = SOIL_LAYERS[dataset]
        image = ee.Image(f"{ISDA_BASE}/{dataset_name}")
        band = image.select(band_name)

        # Apply scaling
        scale_factor = SOIL_SCALING.get(dataset, 1)
        if scale_factor != 1:
            band = band.multiply(scale_factor)
        clipped = band.clip(geometry)
        # 🔹 Compute 2nd and 98th percentile
        percentiles = clipped.reduceRegion(
            reducer=ee.Reducer.percentile([2, 98]),
            geometry=geometry,
            scale=250,
            maxPixels=1e13,
            bestEffort=True,
        )
        stats = percentiles.getInfo()
        if not stats:
            continue
        values = list(stats.values())
        min_val = values[0]
        max_val = values[1]
        # Fallback if invalid
        if min_val is None or max_val is None:
            continue
        # Avoid zero stretch
        if min_val == max_val:
            max_val = min_val + 0.01
        map_id = clipped.getMapId({
            "min": min_val,
            "max": max_val,
            "palette": [
                "blue",
                "cyan",
                "yellow",
                "orange",
                "red"
            ],
        })
        tiles[dataset] = map_id["tile_fetcher"].url_format
    return {
        "status": "success",
        "depth": depth,
        "tiles": tiles,
    }