from fastapi import APIRouter
from pydantic import BaseModel
from app.services.nandi.report_service import generate_nandi_report

router = APIRouter()


class NandiSeedRequest(BaseModel):
    lat: float
    lon: float
    season: str = "LongRains"


@router.post("/nandi-seed")
def get_nandi_seed(payload: NandiSeedRequest):
    return generate_nandi_report(
        lat=payload.lat,
        lon=payload.lon,
        season=payload.season
    )