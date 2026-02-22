# app/services/gee/temperature_tiles.py
import ee

ERA5_DAILY = "ECMWF/ERA5_LAND/DAILY_AGGR"

def get_temperature_tiles(
    geometry: ee.Geometry,
    start_date: str,
    end_date: str
) -> dict:

    collection = (
        ee.ImageCollection(ERA5_DAILY)
        .filterDate(start_date, end_date)
        .select("temperature_2m")
    )

    temp_c = (
        collection
        .mean()
        .subtract(273.15)
        .clip(geometry)
    )

    vis_params = {
        "min": 0,
        "max": 40,
        "palette": [
            "#2c7bb6",
            "#abd9e9",
            "#ffffbf",
            "#fdae61",
            "#d7191c"
        ]
    }

    map_dict = temp_c.getMapId(vis_params)

    return {
        "tile_url": map_dict["tile_fetcher"].url_format,
        "vis_params": vis_params
    }