import ee

SENTINEL_2 = "COPERNICUS/S2_SR"


def get_ndvi_summary(
    geometry: ee.Geometry,
    start_date: str,
    end_date: str
) -> dict:
    """
    Returns mean NDVI for a given geometry and date range.
    RAW NDVI values, no interpretation.
    """

    collection = (
        ee.ImageCollection(SENTINEL_2)
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    )

    def add_ndvi(image):
        ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
        return image.addBands(ndvi)

    ndvi_collection = collection.map(add_ndvi)

    ndvi_mean = ndvi_collection.select("NDVI").mean()

    stats = ndvi_mean.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=10,
        bestEffort=True
    )

    return {
        "ndvi_mean": stats.get("NDVI").getInfo(),
        "start_date": start_date,
        "end_date": end_date,
        "scale_m": 10,
        "aggregation": "mean",
        "source": "Sentinel-2 SR (COPERNICUS)"
    }