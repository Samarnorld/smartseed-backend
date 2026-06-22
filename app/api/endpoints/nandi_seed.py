import logging
from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel, Field
from app.core.limiter import limiter
from app.api.deps import get_current_user
from app.api.schemas import SeasonEnum

from app.services.nandi.engine import analyze

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/nandi",
    tags=["Nandi Engine"]
)

class NandiRequest(BaseModel):
    lat: float = Field(..., ge=-5, le=5.5)
    lon: float = Field(..., ge=33.5, le=42)
    season: SeasonEnum


@router.post("/analyze")
@limiter.limit("10/minute")
def run_analysis(request: Request,
    payload: NandiRequest,
    user: dict = Depends(get_current_user)
):
    try:
        logger.info(f"Nandi analysis requested by {user.get('uid')} for {payload.season}")
        return analyze(payload.model_dump())

    except Exception as e:
        logger.error("Nandi analysis failed", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Analysis failed"
        )
