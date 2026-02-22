# app/services/gee/temperature.py
import ee

ERA5_DAILY = "ECMWF/ERA5_LAND/DAILY_AGGR"

def get_temperature_summary(
    geometry: ee.Geometry,
    start_date: str,
    end_date: str
) -> dict:

    collection = (
        ee.ImageCollection(ERA5_DAILY)
        .filterDate(start_date, end_date)
        .select(["temperature_2m", "temperature_2m_max"])
    )

    mean_img = collection.select("temperature_2m").mean()
    max_img = collection.select("temperature_2m_max").max()

    mean_stats = mean_img.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=1000,
        bestEffort=True,
        maxPixels=1e9
    )

    max_stats = max_img.reduceRegion(
        reducer=ee.Reducer.max(),
        geometry=geometry,
        scale=1000,
        bestEffort=True,
        maxPixels=1e9
    )

    mean_c = ee.Number(mean_stats.get("temperature_2m")).subtract(273.15)
    max_c = ee.Number(max_stats.get("temperature_2m_max")).subtract(273.15)

    return {
        "mean_c": mean_c.getInfo(),
        "max_c": max_c.getInfo(),
        "start_date": start_date,
        "end_date": end_date
    }