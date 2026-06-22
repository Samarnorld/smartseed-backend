# app/api/endpoints/boundaries.py
import logging
from fastapi import APIRouter, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from pathlib import Path
import json
from app.core.limiter import limiter
from app.api.schemas import CountyRequest

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Boundaries"])

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data" / "boundaries"


@router.get("/boundaries/counties/{county_name}")
@limiter.limit("30/minute")
def get_county_boundary(request: Request, county_name: str):
    """Get county boundary data."""
    if county_name.lower() != "nandi":
        logger.warning(f"Boundary request for non-existent county: {county_name}")
        raise HTTPException(status_code=404, detail="County not found")

    path = DATA_DIR / "nandi_county.geojson"

    try:
        with open(path, "r", encoding="utf-8") as f:
            logger.info(f"County boundary requested for: {county_name}")
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"County boundary file not found: {path}")
        raise HTTPException(status_code=500, detail="Data unavailable")
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in county boundary file: {path}")
        raise HTTPException(status_code=500, detail="Data unavailable")


@router.get("/boundaries/wards")
@limiter.limit("30/minute")
def get_wards(request: Request, county: str = Query(...)):
    """Get ward boundaries for a county."""
    if county.lower() != "nandi":
        logger.warning(f"Ward boundary request for non-existent county: {county}")
        raise HTTPException(status_code=404, detail="County not found")

    path = DATA_DIR / "nandi_wards.geojson"

    try:
        with open(path, "r", encoding="utf-8") as f:
            logger.info(f"Ward boundaries requested for: {county}")
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Ward boundary file not found: {path}")
        raise HTTPException(status_code=500, detail="Data unavailable")
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in ward boundary file: {path}")
        raise HTTPException(status_code=500, detail="Data unavailable")
