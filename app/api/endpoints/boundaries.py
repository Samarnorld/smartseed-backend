from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pathlib import Path
import json

router = APIRouter()

DATA_DIR = Path("data/boundaries")

@router.get("/boundaries/counties/{county_name}")
def get_county_boundary(county_name: str):
    if county_name.lower() != "nandi":
        return JSONResponse(
            status_code=404,
            content={"error": "County not found"}
        )

    path = DATA_DIR / "nandi_county.geojson"

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/boundaries/wards")
def get_wards(county: str = Query(...)):
    if county.lower() != "nandi":
        return JSONResponse(
            status_code=404,
            content={"error": "County not found"}
        )

    path = DATA_DIR / "nandi_wards.geojson"

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
