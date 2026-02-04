import ee

ERA5_DAILY = "ECMWF/ERA5_LAND/DAILY_AGGR"


def get_temperature_tiles(
    geometry: ee.Geometry,
    start_date: str,
    end_date: str
) -> dict:
    """
    Returns map tiles for mean 2m air temperature (°C)
    """

    collection = (
        ee.ImageCollection(ERA5_DAILY)
        .filterDate(start_date, end_date)
        .select("temperature_2m")
    )

    # Mean temperature over time
    temp_img = collection.mean().clip(geometry)

    # Convert Kelvin → Celsius
    temp_c = temp_img.subtract(273.15)

    vis_params = {
        "min": 10,
        "max": 35,
        "palette": [
            "#2c7bb6",
            "#abd9e9",
            "#ffffbf",
            "#fdae61",
            "#d7191c"
        ]
    }

    map_id = temp_c.getMapId(vis_params)

    # Get tile URL template
    tile_url = map_id["tile_fetcher"].url_format

    # Ensure token is attached (REQUIRED for browser access)
    if "token=" not in tile_url:
        tile_url = f"{tile_url}?token={map_id['token']}"

    return {
        "mapid": map_id["mapid"],
        "token": map_id["token"],
        "tile_url": tile_url,
        "vis_params": vis_params
    }
