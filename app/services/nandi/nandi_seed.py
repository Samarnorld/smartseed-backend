from fastapi import APIRouter
from app.services.nandi.report_service import generate_report

router = APIRouter()

@router.post("/nandi/seed-report")
def seed_report(payload: dict):
    return generate_report(payload)