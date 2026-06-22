# This module provides an API endpoint to determine the ward and county based on a given latitude and longitude.
# It uses the Shapely library to check if the point defined by the latitude and longitude falls within any of the ward polygons defined in the Nandi County GeoJSON file.
import logging
from fastapi import APIRouter, Query, Depends, HTTPException, Request
from shapely.geometry import shape, Point
from pathlib import Path
import json
from app.core.limiter import limiter
from app.api.deps import get_current_user
from app.api.schemas import LocationRequest

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Location"])

BASE_DIR = Path(__file__).resolve().parents[3]
WARD_FILE = BASE_DIR / "data" / "boundaries" / "nandi_wards.geojson"

@router.get("/ward-from-point")
@limiter.limit("30/minute")
def ward_from_point(request: Request, 
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    user: dict = Depends(get_current_user)
):
    """Get ward and county for a given latitude/longitude. Requires authentication."""
    try:
        with open(WARD_FILE, "r", encoding="utf-8") as f:
            wards = json.load(f)

        point = Point(lon, lat)

        for feature in wards["features"]:
            polygon = shape(feature["geometry"])

            if polygon.contains(point):
                logger.info(f"Location query: lat={lat}, lon={lon} -> {feature['properties']['NAME']}")
                return {
                    "ward": feature["properties"]["NAME"],
                    "county": feature["properties"]["COUNTY_NAM"]
                }
        
        logger.info(f"Location query outside coverage: lat={lat}, lon={lon}")
        return {"ward": None, "county": None}
    
    except FileNotFoundError:
        logger.error(f"Ward boundary file not found: {WARD_FILE}")
        raise HTTPException(status_code=500, detail="Data unavailable")
    except Exception as e:
        logger.error(f"Ward lookup failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Ward lookup failed")
