import ee

ERA5_DAILY = "ECMWF/ERA5_LAND/DAILY_AGGR"


def get_temperature_tiles(
    geometry: ee.Geometry,
    start_date: str,
    end_date: str
) -> dict:
    """
    Returns Earth Engine map tiles for mean 2m air temperature (°C)
    within the given geometry and date range.
    """

    collection = (
        ee.ImageCollection(ERA5_DAILY)
        .filterDate(start_date, end_date)
        .select("temperature_2m")
    )

    # Average temperature across the selected time period
    temp_img = collection.mean().clip(geometry)

    # Convert Kelvin → Celsius
    temp_c = temp_img.subtract(273.15)

    # Better visualization range for East Africa
    vis_params = {
        "min": 0,
        "max": 40,
        "palette": [
            "#2c7bb6",  # cool
            "#abd9e9",
            "#ffffbf",
            "#fdae61",
            "#d7191c"   # hot
        ]
    }

    map_id = temp_c.getMapId(vis_params)

    return {
        "mapid": map_id["mapid"],  # optional metadata
        "tile_url": map_id["tile_fetcher"].url_format,  
        "vis_params": vis_params
    }
