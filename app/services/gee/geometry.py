import ee

DEFAULT_POINT_BUFFER_METERS = 250

def geojson_to_ee(
    geojson: dict,
    point_buffer_m: int = DEFAULT_POINT_BUFFER_METERS
) -> ee.Geometry:
    """
    Convert GeoJSON into ee.Geometry.
    Supports Point, Polygon, MultiPolygon, Feature, FeatureCollection.
    """

    if not isinstance(geojson, dict):
        raise ValueError("GeoJSON must be a dictionary")

    geo_type = geojson.get("type")

    if not geo_type:
        raise ValueError("Invalid GeoJSON: missing 'type'")

    # Feature wrapper
    if geo_type == "Feature":
        geometry = geojson.get("geometry")
        if not geometry:
            raise ValueError("Feature has no geometry")
        return geojson_to_ee(geometry, point_buffer_m)

    # FeatureCollection
    if geo_type == "FeatureCollection":
        features = geojson.get("features", [])
        if not features:
            raise ValueError("FeatureCollection has no features")

        ee_geoms = [
            geojson_to_ee(f["geometry"], point_buffer_m)
            for f in features
            if f.get("geometry")
        ]

        # Union all geometries into one
        geom = ee_geoms[0]
        for g in ee_geoms[1:]:
            geom = geom.union(g)

        return geom

    # Point
    if geo_type == "Point":
        coords = geojson.get("coordinates")
        if not coords:
            raise ValueError("Point missing coordinates")

        return ee.Geometry.Point(coords).buffer(point_buffer_m)

    # Polygon / MultiPolygon
    if geo_type in ("Polygon", "MultiPolygon"):
        return ee.Geometry(geojson)

    raise ValueError(f"Unsupported GeoJSON type: {geo_type}")
