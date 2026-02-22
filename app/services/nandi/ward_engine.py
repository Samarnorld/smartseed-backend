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
            return {"error": "Ward recommendation file not found"}

        factors_df = pd.read_csv(WARD_FACTORS_PATH)
        recomm_df = pd.read_csv(WARD_RECOMM_PATH)

        # Normalize column names
        factors_df.columns = [c.strip() for c in factors_df.columns]
        recomm_df.columns = [c.strip() for c in recomm_df.columns]

        # Filter ward
        factors_row = factors_df[
            factors_df["Ward"].str.lower() == ward_name.lower()
        ]

        recomm_row = recomm_df[
            recomm_df["Ward"].str.lower() == ward_name.lower()
        ]

        if factors_row.empty or recomm_row.empty:
            return {"error": "Ward not found"}

        factors_row = factors_row.iloc[0]
        recomm_row = recomm_row.iloc[0]

        prefix = "LR_" if season == "LongRains" else "SR_"

        # -------------------------
        # Suitability & Seeds
        # -------------------------
        suitability = recomm_row.get(f"{prefix}Suitability")
        seeds = recomm_row.get(f"{prefix}Seeds")
        fertiliser_advice = recomm_row.get(f"{prefix}Fertiliser")
        risk_warning_text = recomm_row.get(f"{prefix}Risk_Warnings")

        # Convert seed string to list if needed
        if isinstance(seeds, str):
            seed_list = [s.strip() for s in seeds.split(",")]
        else:
            seed_list = []

        # -------------------------
        # Risk breakdown
        # -------------------------
        failure_pct = factors_row.get(f"{prefix}Overall_Failure_ward_pct")
        cold = factors_row.get(f"{prefix}Cold_Risk_ward_pct")
        heat = factors_row.get(f"{prefix}Heat_Risk_ward_pct")
        drought = factors_row.get(f"{prefix}Drought_Risk_ward_pct")

        if failure_pct is None:
            risk_level = "Unknown"
        elif failure_pct > 50:
            risk_level = "High"
        elif failure_pct > 20:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        # -------------------------
        # Soil values
        # -------------------------
        soil_values = {
            "stone_content": factors_row.get(f"{prefix}stone_content_ward_avg"),
            "bedrock_depth": factors_row.get(f"{prefix}bedrock_depth_ward_avg"),
            "texture_score": factors_row.get(f"{prefix}texture_score"),
        }

        # -------------------------
        # Human explanation
        # -------------------------
        explanation = (
            f"{ward_name} ward has {risk_level} production risk during {season}. "
            f"Overall failure probability is {round(failure_pct,2)}%. "
            f"Recommended seeds: {', '.join(seed_list)}."
        )

        return {
            "ward": ward_name,
            "season": season,
            "seed_recommendation": {
                "ward_suitability": suitability,
                "overall_failure_probability_percent": failure_pct,
                "recommended_varieties": seed_list,
                "planting_window": recomm_row.get(f"{prefix}Planting_Window")
            },
            "fertilizer": {
                "soil_values": soil_values,
                "recommended_fertiliser": fertiliser_advice
            },
            "advisory": {
                "risk_level": risk_level,
                "risk_breakdown_percent": {
                    "cold": cold,
                    "heat": heat,
                    "drought": drought
                },
                "risk_warning_text": risk_warning_text,
                "explanation": explanation
            }
        }