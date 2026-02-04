import ee

SRTM = "USGS/SRTMGL1_003"


def get_elevation_tiles(geometry: ee.Geometry) -> dict:
    """
    Returns map tiles URL for elevation (meters)
    """

    dem = (
        ee.Image(SRTM)
        .select("elevation")
        .clip(geometry)
    )

    vis_params = {
    "min": 0,
    "max": 3000,
    "palette": [
        "#0b3d02",  # dark green lowlands
        "#1f7a1f",
        "#4caf50",
        "#cddc39",
        "#ffeb3b",
        "#ff9800",
        "#ff5722",
        "#795548",
        "#ffffff"   # mountain peaks
    ]
}

    map_id = dem.getMapId(vis_params)

    return {
        "tile_url": map_id["tile_fetcher"].url_format
    }
