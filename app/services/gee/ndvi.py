import ee

# Sentinel-2 surface reflectance
S2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"


def get_mean_ndvi(
    geometry: ee.Geometry,
    start_date: str,
    end_date: str
) -> dict:
    """
    Returns mean NDVI over a geometry for a given time range.
    """

    collection = (
        ee.ImageCollection(S2_COLLECTION)
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    )

    # Compute NDVI per image
    ndvi_collection = collection.map(
        lambda img: img.normalizedDifference(["B8", "B4"]).rename("NDVI")
    )

    mean_ndvi = ndvi_collection.mean()

    stats = mean_ndvi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=10,
        bestEffort=True,
        maxPixels=1e13
    )

    return {
        "mean_ndvi": stats.get("NDVI").getInfo(),
        "start_date": start_date,
        "end_date": end_date,
        "source": "Sentinel-2 (COPERNICUS)"
    }