# app/api/endpoints/nandi_recommendations.py
from fastapi import APIRouter, Query, HTTPException
from app.services.nandi.seed_engine import NandiSeedEngine
from app.services.nandi.fertilizer_engine import NandiFertilizerEngine
from app.services.nandi.advisory_engine import NandiAdvisoryEngine
from app.services.nandi.ward_engine import NandiWardEngine
from app.services.nandi.county_engine import NandiCountyEngine

router = APIRouter()

# Pixel-based recommendation
@router.get("/nandi/recommendation")
def get_nandi_recommendation(
    lon: float = Query(...),
    lat: float = Query(...),
    season: str = Query(..., pattern="^(LongRains|ShortRains)$")
):

    seed = NandiSeedEngine.recommend(lon, lat, season)

    if "error" in seed:
        raise HTTPException(status_code=400, detail=seed["error"])

    fertilizer = NandiFertilizerEngine.recommend(lon, lat, season)
    advisory = NandiAdvisoryEngine.assess(lon, lat, season)

    return {
        "location": {"lon": lon, "lat": lat},
        "aggregation_level": "pixel",
        "season": season,
        "seed_recommendation": seed,
        "fertilizer": fertilizer,
        "advisory": advisory
    }

# Ward-level aggregated
@router.get("/nandi/ward-recommendation")
def get_ward_recommendation(
    ward_name: str = Query(...),
    season: str = Query(..., pattern="^(LongRains|ShortRains)$")
):

    result = NandiWardEngine.get_ward_recommendation(ward_name, season)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return {
        "aggregation_level": "ward",
        "ward": ward_name,
        "season": season,
        "data": result
    }

# County-level aggregated
@router.get("/nandi/county-summary")
def get_county_summary(
    season: str = Query(..., pattern="^(LongRains|ShortRains)$")
):

    result = NandiCountyEngine.get_county_summary(season)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return {
        "aggregation_level": "county",
        "county": "Nandi",
        "season": season,
        "data": result
    }

# ADDED: Seed Catalog Endpoint
@router.get("/nandi/seeds")
def get_seed_catalog():

    result = NandiSeedEngine.get_seed_catalog()

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return {
        "aggregation_level": "seed_catalog",
        "data": result
    }