# app/services/nandi/seed_engine.py
import pandas as pd
from typing import Dict
from .config import SEED_DATA, suitability_paths
from .raster_sampling import sample_raster

class NandiSeedEngine:

    @staticmethod
    def recommend(lon: float, lat: float, season: str) -> Dict:

        mean_path, std_path, overall_path, _ = suitability_paths(season)

        suitability = sample_raster(mean_path, lon, lat)
        uncertainty = sample_raster(std_path, lon, lat)
        overall_failure = sample_raster(overall_path, lon, lat)

        if suitability is None:
            return {"error": "Location outside Nandi coverage"}

        df = pd.read_excel(SEED_DATA)

        risk_penalty = (overall_failure or 0) * 0.5

        df["ranking_score"] = (
            suitability
            - (uncertainty or 0) * 0.4
            - risk_penalty
        )

        top3 = df.sort_values("ranking_score", ascending=False).head(3)

        return {
            "suitability_score": round(suitability, 3),
            "uncertainty": round(uncertainty or 0, 3),
            "overall_failure_probability": round(overall_failure or 0, 3),
            "recommended_varieties": top3["Variety"].tolist()
        }

    # Seed Catalog Method
    @staticmethod
    def get_seed_catalog() -> Dict:
        """
        Returns all seed varieties being analyzed and total count.
        Does NOT affect recommendation logic.
        """

        df = pd.read_excel(SEED_DATA)

        if "Variety" not in df.columns:
            return {"error": "Variety column not found in seed dataset"}

        varieties = (
            df["Variety"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        varieties_sorted = sorted(varieties)

        return {
            "total_seed_varieties": len(varieties_sorted),
            "seed_varieties": varieties_sorted
        }