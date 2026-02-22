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
        confidence = sample_raster(conf_path, lon, lat)

        risk_paths = risk_factor_paths(season)

        breakdown = {
            key: sample_raster(path, lon, lat)
            for key, path in risk_paths.items()
        }

        if suitability is None:
            return {"error": "Location outside Nandi coverage"}

        if overall_failure is None:
            risk_level = "Unknown"
        elif overall_failure < 0.2:
            risk_level = "Low"
        elif overall_failure < 0.5:
            risk_level = "Moderate"
        else:
            risk_level = "High"

        return {
            "suitability": round(suitability, 3) if suitability else None,
            "uncertainty": round(uncertainty or 0, 3),
            "confidence_tier": confidence,
            "overall_failure_probability": round(overall_failure or 0, 3),
            "risk_level": risk_level,
            "risk_breakdown": breakdown,
        }