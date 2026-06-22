# app/api/endpoints/nandi_recommendations.py
import logging
from fastapi import APIRouter, Query, HTTPException, Request, Depends
from app.core.limiter import limiter
from app.api.deps import get_current_user
from app.api.schemas import NandiPixelRequest, NandiWardRequest, NandiCountyRequest, SeasonEnum
from app.services.nandi.seed_engine import NandiSeedEngine
from app.services.nandi.fertilizer_engine import NandiFertilizerEngine
from app.services.nandi.advisory_engine import NandiAdvisoryEngine
from app.services.nandi.ward_engine import NandiWardEngine
from app.services.nandi.county_engine import NandiCountyEngine

logger = logging.getLogger(__name__)

router = APIRouter()

# Pixel-based recommendation
@router.get("/nandi/recommendation")
@limiter.limit("20/minute")
def get_nandi_recommendation(request: Request,
    lon: float = Query(..., ge=-180, le=180),
    lat: float = Query(..., ge=-90, le=90),
    season: SeasonEnum = Query(...),
    user: dict = Depends(get_current_user)
):
    """Get pixel-level seed and fertilizer recommendations. Requires authentication."""
    try:
        logger.info(f"Nandi recommendation requested by {user.get('uid')} at ({lon}, {lat})")
        
        seed = NandiSeedEngine.recommend(lon, lat, season.value)

        if "error" in seed:
            logger.warning(f"Seed recommendation error: {seed['error']}")
            raise HTTPException(status_code=400, detail=seed["error"])

        fertilizer = NandiFertilizerEngine.recommend(lon, lat, season.value)
        advisory = NandiAdvisoryEngine.assess(lon, lat, season.value)

        return {
            "location": {"lon": lon, "lat": lat},
            "aggregation_level": "pixel",
            "season": season.value,
            "seed_recommendation": seed,
            "fertilizer": fertilizer,
            "advisory": advisory
        }
    except Exception as e:
        logger.error(f"Recommendation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")

# Ward-level aggregated
@router.get("/nandi/ward-recommendation")
@limiter.limit("20/minute")
def get_ward_recommendation(request: Request,
    ward_name: str = Query(..., min_length=1, max_length=100),
    season: SeasonEnum = Query(...),
    user: dict = Depends(get_current_user)
):
    """Get ward-level aggregated recommendations. Requires authentication."""
    try:
        logger.info(f"Ward recommendation requested by {user.get('uid')} for {ward_name}")
        
        result = NandiWardEngine.get_ward_recommendation(ward_name, season.value)

        if "error" in result:
            logger.warning(f"Ward lookup error: {result['error']}")
            raise HTTPException(status_code=404, detail=result["error"])

        return {
            "aggregation_level": "ward",
            "ward": ward_name,
            "season": season.value,
            "data": result
        }
    except Exception as e:
        logger.error(f"Ward recommendation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")

# County-level aggregated
@router.get("/nandi/county-summary")
@limiter.limit("20/minute")
def get_county_summary(request: Request,
    season: SeasonEnum = Query(...),
    user: dict = Depends(get_current_user)
):
    """Get county-level aggregated summary. Requires authentication."""
    try:
        logger.info(f"County summary requested by {user.get('uid')}")
        
        result = NandiCountyEngine.get_county_summary(season.value)

        if "error" in result:
            logger.warning(f"County summary error: {result['error']}")
            raise HTTPException(status_code=404, detail=result["error"])

        return {
            "aggregation_level": "county",
            "county": "Nandi",
            "season": season.value,
            "data": result
        }
    except Exception as e:
        logger.error(f"County summary failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")

# Seed Catalog Endpoint
@router.get("/nandi/seeds")
@limiter.limit("20/minute")
def get_seed_catalog(request: Request,
    user: dict = Depends(get_current_user)
):
    """Get seed catalog. Requires authentication."""
    try:
        logger.info(f"Seed catalog requested by {user.get('uid')}")
        
        result = NandiSeedEngine.get_seed_catalog()

        if "error" in result:
            logger.error(f"Seed catalog error: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])

        return {
            "aggregation_level": "seed_catalog",
            "data": result
        }
    except Exception as e:
        logger.error(f"Seed catalog failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
