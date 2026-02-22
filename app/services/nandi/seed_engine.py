# app/services/nandi/seed_engine.py
import pandas as pd
from typing import Dict
from .config import SEED_DATA, suitability_paths
from .raster_sampling import sample_raster

class NandiSeedEngine:

    @staticmethod
    def recommend(lon: float, lat: float, season: str) -> Dict:

        mean_path, std_path, _ = suitability_paths(season)

        suitability = sample_raster(mean_path, lon, lat)
        uncertainty = sample_raster(std_path, lon, lat)

        if suitability is None:
            return {"error": "Location outside Nandi coverage"}

        df = pd.read_excel(SEED_DATA)

        # Simple ranking logic (replace later with ML weights)
        df["ranking_score"] = suitability - (uncertainty or 0) * 0.4

        top3 = df.sort_values("ranking_score", ascending=False).head(3)

        return {
            "suitability_score": round(suitability, 3),
            "uncertainty": round(uncertainty or 0, 3),
            "recommended_varieties": top3["Variety"].tolist()
        }