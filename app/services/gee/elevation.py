import ee

SRTM = "USGS/SRTMGL1_003"

def get_elevation_and_slope(geometry: ee.Geometry) -> dict:
    """
    Returns elevation (m) and slope (degrees)
    """

    dem = ee.Image(SRTM).clip(geometry)

    elevation = dem.select("elevation")
    slope = ee.Terrain.slope(elevation)

    elev_stats = elevation.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=30,
        bestEffort=True
    )

    slope_stats = slope.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=30,
        bestEffort=True
    )

    return {
        "elevation_mean_m": elev_stats.get("elevation").getInfo(),
        "slope_mean_deg": slope_stats.get("slope").getInfo()
    }
