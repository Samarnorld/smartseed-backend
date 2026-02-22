import pandas as pd
import os
import re
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

        factors_df = pd.read_csv(WARD_FACTORS_PATH)
        recomm_df = pd.read_csv(WARD_RECOMM_PATH)

        factors_row = factors_df[
            factors_df["Ward"].str.lower() == ward_name.lower()
        ].iloc[0]

        recomm_row = recomm_df[
            recomm_df["Ward"].str.lower() == ward_name.lower()
        ].iloc[0]

        prefix = "LR_" if season == "LongRains" else "SR_"

        # -------------------------
        # Suitability (extract numeric %)
        # -------------------------
        suitability_text = recomm_row.get(f"{prefix}Suitability", "")

        match = re.search(r"(\d+(\.\d+)?)%", str(suitability_text))
        suitability_percent = float(match.group(1)) if match else None

        # -------------------------
        # Seeds (split by |)
        # -------------------------
        seeds_raw = recomm_row.get(f"{prefix}Seeds", "")

        if isinstance(seeds_raw, str):
            seed_list = [s.strip() for s in seeds_raw.split("|")]
        else:
            seed_list = []

        # -------------------------
        # Risk
        # -------------------------
        failure_pct = factors_row.get(f"{prefix}Overall_Failure_ward_pct")

        if failure_pct > 50:
            risk_level = "High"
        elif failure_pct > 20:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        # -------------------------
        # Soil
        # -------------------------
        soil_values = {
            "stone_content": factors_row.get(f"{prefix}stone_content_ward_avg"),
            "bedrock_depth": factors_row.get(f"{prefix}bedrock_depth_ward_avg"),
            "texture_score": factors_row.get(f"{prefix}texture_score"),
        }

        return {
            "ward": ward_name,
            "season": season,
            "seed_recommendation": {
                "suitability_percent": suitability_percent,
                "suitability_text": suitability_text,
                "overall_failure_probability_percent": failure_pct,
                "recommended_varieties": seed_list,
                "planting_window": recomm_row.get(f"{prefix}Planting_Window")
            },
            "fertilizer": {
                "soil_values": soil_values,
                "recommended_fertiliser": recomm_row.get(f"{prefix}Fertiliser")
            },
            "advisory": {
                "risk_level": risk_level,
                "risk_breakdown_percent": {
                    "cold": factors_row.get(f"{prefix}Cold_Risk_ward_pct"),
                    "heat": factors_row.get(f"{prefix}Heat_Risk_ward_pct"),
                    "drought": factors_row.get(f"{prefix}Drought_Risk_ward_pct")
                },
                "risk_warning_text": recomm_row.get(f"{prefix}Risk_Warnings")
            }
        }