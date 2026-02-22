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


class NandiWardEngine:

    @staticmethod
    def get_ward_recommendation(ward_name: str, season: str) -> Dict:

        if not os.path.exists(WARD_FACTORS_PATH):
            return {"error": "Ward factors file not found"}

        df = pd.read_csv(WARD_FACTORS_PATH)

        df.columns = [c.strip() for c in df.columns]

        ward_df = df[df["Ward"].str.lower() == ward_name.lower()]

        if ward_df.empty:
            return {"error": "Ward not found"}

        row = ward_df.iloc[0]

        prefix = "LR_" if season == "LongRains" else "SR_"

        # -------------------------
        # Suitability & Risk
        # -------------------------
        suitability = row.get(f"{prefix}Suitability_Mean")
        failure = row.get(f"{prefix}Failure_Probability")

        cold = row.get(f"{prefix}Cold_Risk_ward_pct")
        heat = row.get(f"{prefix}Heat_Risk_ward_pct")
        drought = row.get(f"{prefix}Drought_Risk_ward_pct")

        # -------------------------
        # Soil values (ward averages)
        # -------------------------
        soil_values = {
            "stone_content": row.get(f"{prefix}stone_content_ward_avg"),
            "bedrock_depth": row.get(f"{prefix}bedrock_depth_ward_avg"),
            "texture_score": row.get(f"{prefix}texture_score"),
        }

        # -------------------------
        # Risk classification
        # -------------------------
        if failure is None:
            risk_level = "Unknown"
        elif failure > 50:
            risk_level = "High"
        elif failure > 20:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        explanation = (
            f"{ward_name} ward shows {risk_level} seasonal production risk "
            f"during {season}. "
            f"Drought risk: {drought}%, Heat risk: {heat}%, Cold risk: {cold}%."
        )

        return {
            "ward": ward_name,
            "season": season,
            "seed_recommendation": {
                "mean_suitability_score": suitability,
                "overall_failure_probability_percent": failure
            },
            "fertilizer": {
                "soil_values": soil_values
            },
            "advisory": {
                "risk_level": risk_level,
                "risk_breakdown_percent": {
                    "cold": cold,
                    "heat": heat,
                    "drought": drought
                },
                "explanation": explanation
            }
        }