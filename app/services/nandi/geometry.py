# app/services/nandi/geometry.py
import geopandas as gpd
from shapely.geometry import shape, Point

WARD_PATH = "data/02_NandiSeedRecommender2/WardAggregatedData/Nandi_Ward_Aggregation.geojson"

wards_gdf = gpd.read_file(WARD_PATH)


def from_point(lat: float, lon: float):
    return Point(lon, lat).buffer(0.001)


def from_polygon(geojson: dict):
    return shape(geojson)


def from_ward(ward_name: str):
    ward = wards_gdf[wards_gdf["NAME"] == ward_name]
    if ward.empty:
        raise ValueError("Ward not found")
    return ward.geometry.iloc[0]


def from_county():
    return wards_gdf.unary_union