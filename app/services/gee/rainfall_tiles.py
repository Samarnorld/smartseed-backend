# services/gee/rainfall_tiles.py
import ee
from datetime import datetime

def get_rainfall_tiles(
    geometry: ee.Geometry,
    start_date: str,
    end_date: str
):
    """
    Returns a GEE XYZ tile URL for CHIRPS rainfall
    """

    # CHIRPS daily rainfall
    collection = (
        ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
        .filterDate(start_date, end_date)
        .filterBounds(geometry)
    )

    # Total rainfall over period
    rainfall = collection.sum().clip(geometry)

    # Visualization parameters
    vis_params = {
        "min": 0,
        "max": 2000,  # mm
        "palette": [
            "ffffff",
            "ccebc5",
            "a8ddb5",
            "7bccc4",
            "4eb3d3",
            "2b8cbe",
            "08589e"
        ]
    }

    map_id = rainfall.getMapId(vis_params)

    return {
        "mapid": map_id["mapid"],
        "token": map_id["token"],
        "tile_url": map_id["tile_fetcher"].url_format
    }
