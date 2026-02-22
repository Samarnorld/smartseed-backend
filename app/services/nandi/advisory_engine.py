# app/services/nandi/advisory_engine.py
# NandiAdvisoryEngine is responsible for assessing the suitability and risk
# of maize cultivation at a given location and season based on precomputed
# raster data. It samples the relevant rasters to provide a comprehensive
# advisory report, including suitability score, uncertainty, confidence score,
# confidence tier, overall failure probability, and a breakdown of risk factors.

from typing import Dict
from .config import suitability_paths, risk_factor_paths
from .raster_sampling import sample_raster


class NandiAdvisoryEngine:

    @staticmethod
    def assess(lon: float, lat: float, season: str) -> Dict:

        mean_path, std_path, overall_path, conf_path = suitability_paths(season)

        suitability = sample_raster(mean_path, lon, lat)
        uncertainty = sample_raster(std_path, lon, lat)
        overall_failure = sample_raster(overall_path, lon, lat)
        confidence_score = sample_raster(conf_path, lon, lat)

        risk_paths = risk_factor_paths(season)

        breakdown = {
            key: sample_raster(path, lon, lat)
            for key, path in risk_paths.items()
        }

        if suitability is None:
            return {"error": "Location outside Nandi coverage"}

        # Risk classification
        if overall_failure is None:
            risk_level = "Unknown"
        elif overall_failure < 0.2:
            risk_level = "Low"
        elif overall_failure < 0.5:
            risk_level = "Moderate"
        else:
            risk_level = "High"

        # Convert continuous confidence score into tier
        if confidence_score is not None:
            if confidence_score < 0.05:
                confidence_tier = 1  # Very High Confidence
            elif confidence_score < 0.1:
                confidence_tier = 2
            elif confidence_score < 0.2:
                confidence_tier = 3
            else:
                confidence_tier = 4
        else:
            confidence_tier = None

        return {
            "suitability": round(suitability, 3),
            "uncertainty": round(uncertainty or 0, 3),
            "confidence_score": round(confidence_score or 0, 4),
            "confidence_tier": confidence_tier,
            "overall_failure_probability": round(overall_failure or 0, 3),
            "risk_level": risk_level,
            "risk_breakdown": breakdown,
        }