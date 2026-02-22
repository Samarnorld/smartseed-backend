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

        # Apply scaling for visualization
        scale_factor = SOIL_SCALING.get(dataset, 1)
        if scale_factor != 1:
            band = band.multiply(scale_factor)

        clipped = band.clip(geometry)

        vis = SOIL_VIS.get(dataset, {"min": 0, "max": 100})

        map_id = clipped.getMapId({
            "min": vis["min"],
            "max": vis["max"],
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