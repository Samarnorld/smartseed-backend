from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from pathlib import Path
import json
from app.api.deps import get_current_user

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data" / "boundaries"

@router.get("/boundaries/counties/{county_name}")
def get_county_boundary(
    county_name: str,
    user=Depends(get_current_user)
):
    if county_name.lower() != "nandi":
        return JSONResponse(
            status_code=404,
            content={"error": "County not found"}
        )

    path = DATA_DIR / "nandi_county.geojson"

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/boundaries/wards")
def get_wards(
    county: str = Query(...),
    user=Depends(get_current_user)
):
    if county.lower() != "nandi":
        return JSONResponse(
            status_code=404,
            content={"error": "County not found"}
        )

    path = DATA_DIR / "nandi_wards.geojson"

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
