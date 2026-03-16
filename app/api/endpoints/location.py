# This module provides an API endpoint to determine the ward and county based on a given latitude and longitude.
# It uses the Shapely library to check if the point defined by the latitude and longitude falls within any of the ward polygons defined in the Nandi County GeoJSON file.
from fastapi import APIRouter, Query
from shapely.geometry import shape, Point
from pathlib import Path
import json

router = APIRouter(tags=["Location"])

BASE_DIR = Path(__file__).resolve().parents[3]
WARD_FILE = BASE_DIR / "data" / "boundaries" / "nandi_wards.geojson"
@router.get("/ward-from-point")
def ward_from_point(lat: float = Query(...), lon: float = Query(...)):

    with open(WARD_FILE, "r", encoding="utf-8") as f:
        wards = json.load(f)

    point = Point(lon, lat)

    for feature in wards["features"]:
        polygon = shape(feature["geometry"])

        if polygon.contains(point):
            return {
                "ward": feature["properties"]["NAME"],
                "county": feature["properties"]["COUNTY_NAM"]
            }

    return {"ward": None}