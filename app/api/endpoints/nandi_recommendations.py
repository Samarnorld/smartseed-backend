# app/api/endpoints/nandi_recommendations.py
from fastapi import APIRouter, Query, HTTPException
from app.services.nandi.seed_engine import NandiSeedEngine
from app.services.nandi.fertilizer_engine import NandiFertilizerEngine
from app.services.nandi.advisory_engine import NandiAdvisoryEngine

router = APIRouter()

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
        "season": season,
        "seed_recommendation": seed,
        "fertilizer": fertilizer,
        "advisory": advisory
    }