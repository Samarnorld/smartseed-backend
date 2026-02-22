# app/services/nandi/ward_engine.py

import pandas as pd
import os
from typing import Dict
from .config import BASE_PATH


WARD_FACTORS_PATH = os.path.join(
    BASE_PATH,
    "WardAggregatedData",
    "Nandi_Ward_Factors.csv"
)

WARD_RECOMM_PATH = os.path.join(
    BASE_PATH,
    "WardAggregatedData",
    "Nandi_Ward_Recommendations.csv"
)


class NandiWardEngine:

    @staticmethod
    def get_ward_recommendation(ward_name: str, season: str) -> Dict:

        if not os.path.exists(WARD_FACTORS_PATH):
            return {"error": "Ward factors file not found"}

        if not os.path.exists(WARD_RECOMM_PATH):
            return {"error": "Ward recommendations file not found"}

        factors_df = pd.read_csv(WARD_FACTORS_PATH)
        recomm_df = pd.read_csv(WARD_RECOMM_PATH)

        factors = factors_df[
            (factors_df["Ward"] == ward_name) &
            (factors_df["Season"] == season)
        ]

        recomm = recomm_df[
            (recomm_df["Ward"] == ward_name) &
            (recomm_df["Season"] == season)
        ]

        if factors.empty:
            return {"error": "Ward not found"}

        row = factors.iloc[0]

        suitability = row.get("Suitability_Mean")
        failure = row.get("Failure_Probability")

        # Soil raw averages
        soil_values = {
            "N": row.get("total_nitrogen"),
            "P": row.get("phosphorus"),
            "K": row.get("potassium"),
            "pH": row.get("ph"),
            "organic_carbon": row.get("organic_carbon"),
            "magnesium": row.get("magnesium"),
            "zinc": row.get("zinc"),
            "bedrock_depth": row.get("bedrock_depth"),
            "stone_content": row.get("stone_content"),
            "texture": row.get("texture"),
        }

        # Fertilizer logic (same as pixel)
        advice = []

        if soil_values["N"] and soil_values["N"] < 0.2:
            advice.append("Apply Nitrogen fertilizer (CAN/Urea)")

        if soil_values["P"] and soil_values["P"] < 15:
            advice.append("Apply Phosphorus fertilizer (DAP/TSP)")

        if soil_values["K"] and soil_values["K"] < 100:
            advice.append("Apply Potassium fertilizer (MOP)")

        if soil_values["pH"] and soil_values["pH"] < 5.5:
            advice.append("Apply Agricultural Lime")

        dominant_factor = row.get("Most_Limiting_Factor")

        risk_level = "Low"
        if failure and failure > 0.5:
            risk_level = "High"
        elif failure and failure > 0.2:
            risk_level = "Moderate"

        explanation = (
            f"Ward shows {risk_level} production risk. "
            f"The dominant limiting factor is {dominant_factor}."
        )

        varieties = []
        if not recomm.empty:
            varieties = recomm.iloc[0].get("Top_3_Varieties")

        return {
            "ward": ward_name,
            "season": season,
            "seed_recommendation": {
                "mean_suitability_score": suitability,
                "overall_failure_probability": failure,
                "recommended_varieties": varieties,
            },
            "fertilizer": {
                "soil_values": soil_values,
                "fertilizer_recommendations": advice
            },
            "advisory": {
                "risk_level": risk_level,
                "dominant_limiting_factor": dominant_factor,
                "explanation": explanation
            }
        }