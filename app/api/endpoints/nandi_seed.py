# app/api/endpoints/nandi_seed.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.nandi.raster_engine import get_suitability, get_risks

router = APIRouter()


class NandiRequest(BaseModel):
    lat: float
    lon: float
    season: str = "LongRains"


@router.post("/nandi/suitability")
def nandi_suitability(request: NandiRequest):

    suitability = get_suitability(
        request.lat,
        request.lon,
        request.season
    )

    risks = get_risks(
        request.lat,
        request.lon,
        request.season
    )

    return {
        "location": {
            "lat": request.lat,
            "lon": request.lon
        },
        "suitability": suitability,
        "risks": risks
    }