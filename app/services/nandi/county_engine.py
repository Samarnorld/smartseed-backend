# app/services/nandi/county_engine.py

import json
import os
from typing import Dict
from .config import FINAL_OUTPUTS


COUNTY_PATH = os.path.join(FINAL_OUTPUTS, "County_Averages.json")


class NandiCountyEngine:

    @staticmethod
    def get_county_summary(season: str) -> Dict:

        if not os.path.exists(COUNTY_PATH):
            return {"error": "County averages file not found"}

        with open(COUNTY_PATH, "r") as f:
            data = json.load(f)

        if season not in data:
            return {"error": "Season not found"}

        season_data = data[season]

        scores = season_data.get("scores", {})
        raw = season_data.get("raw", {})

        failure = scores.get("prob_overall_fail")

        risk_level = "Low"
        if failure and failure > 0.5:
            risk_level = "High"
        elif failure and failure > 0.2:
            risk_level = "Moderate"

        dominant_factor = max(
            {
                "heat": scores.get("prob_heat"),
                "drought": scores.get("prob_drought"),
                "flood": scores.get("prob_flood"),
                "cold": scores.get("prob_cold")
            },
            key=lambda k: scores.get(f"prob_{k}") or 0
        )

        explanation = (
            f"County-level {risk_level} production risk. "
            f"Dominant stress factor is {dominant_factor}."
        )

        return {
            "county": "Nandi",
            "season": season,
            "seed_recommendation": {
                "mean_suitability_score": scores.get("temp"),
                "overall_failure_probability": failure
            },
            "fertilizer": {
                "soil_values": raw
            },
            "advisory": {
                "risk_level": risk_level,
                "dominant_limiting_factor": dominant_factor,
                "explanation": explanation
            }
        }