import logging
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from datetime import datetime
import ee

from app.core.limiter import limiter
from app.api.deps import get_current_user, get_geometry
from app.services.gee.temperature_anomaly import (
    get_current_season_overview,
    get_temperature_seasonal_anomaly,
    get_10yr_temperature_trend,
    get_agronomic_interpretation
)
from app.services.cache.redis_cache import (
    get_cache,
    set_cache,
    build_cache_key,
    CACHE_30_DAYS
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/temperature", tags=["Temperature"])
current_year = datetime.utcnow().year

@router.post("/dashboard")
@limiter.limit("20/minute")
def temperature_dashboard(request: Request,
    season: str = Query(...),
    year: int = Query(..., ge=1981, le=current_year),
    geometry: ee.Geometry = Depends(get_geometry),
    user: dict = Depends(get_current_user)
):
    try:
        payload = {
            "geometry": geometry.getInfo(),
            "season": season,
            "year": year
        }
        cache_key = build_cache_key("temperature_dashboard", payload)
        cached = get_cache(cache_key)
        if cached:
            logger.info(f"Cache HIT: temperature_dashboard for {user.get('uid')}")
            return cached

        logger.info(f"Cache MISS: temperature_dashboard for {user.get('uid')}")
        overview = get_current_season_overview(geometry, season, year)
        anomaly = get_temperature_seasonal_anomaly(geometry, season, year)
        trend = get_10yr_temperature_trend(geometry, season, year)
        agronomic = get_agronomic_interpretation(
            mean_temp_c=overview["mean_temp_c"],
            heat_days=overview["heat_stress_days_above_35C"]
        )
        result = {
            "status": "success",
            "dataset": "ERA5-Land",
            "units": "°C",
            "section_a_overview": overview,
            "section_b_anomaly": anomaly,
            "section_c_trend": trend,
            "section_d_agronomic_interpretation": agronomic
        }
        set_cache(cache_key, result, CACHE_30_DAYS)
        return result
    except Exception as e:
        logger.error("Temperature dashboard failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
