# app/services/nandi/advisory_engine.py
from typing import Dict
from .config import suitability_paths
from .raster_sampling import sample_raster
class NandiAdvisoryEngine:

    @staticmethod
    def assess(lon: float, lat: float, season: str) -> Dict:

        _, _, failure_path = suitability_paths(season)

        failure_prob = sample_raster(failure_path, lon, lat)

        if failure_prob is None:
            return {"risk_level": "Unknown"}

        if failure_prob < 0.2:
            risk = "Low Risk"
        elif failure_prob < 0.5:
            risk = "Moderate Risk"
        else:
            risk = "High Risk"

        return {
            "failure_probability": round(failure_prob, 3),
            "risk_level": risk
        }