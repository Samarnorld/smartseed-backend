# app/api/endpoints/nandi_seed.py

from fastapi import APIRouter
from app.services.nandi.engine import analyze

router = APIRouter(prefix="/nandi", tags=["Nandi Engine"])


@router.post("/analyze")
def run_analysis(request: dict):
    return analyze(request)