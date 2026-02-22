# app/services/nandi/ward_engine.py
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

        if not os.path.exists(WARD_FACTORS_PATH):
            return {"error": "Ward factors file not found"}

        if not os.path.exists(WARD_RECOMM_PATH):
            return {"error": "Ward recommendation file not found"}

        factors_df = pd.read_csv(WARD_FACTORS_PATH)
        recomm_df = pd.read_csv(WARD_RECOMM_PATH)

        factors_df.columns = [c.strip() for c in factors_df.columns]
        recomm_df.columns = [c.strip() for c in recomm_df.columns]

        factors_filtered = factors_df[
            factors_df["Ward"].str.lower() == ward_name.lower()
        ]

        recomm_filtered = recomm_df[
            recomm_df["Ward"].str.lower() == ward_name.lower()
        ]

        if factors_filtered.empty or recomm_filtered.empty:
            return {"error": "Ward not found"}

        factors_row = factors_filtered.iloc[0]
        recomm_row = recomm_filtered.iloc[0]

        prefix = "LR_" if season == "LongRains" else "SR_"

        # -------------------------
        # Suitability
        # -------------------------
        suitability_text = recomm_row.get(f"{prefix}Suitability", "")
        match = re.search(r"(\d+(\.\d+)?)%", str(suitability_text))
        suitability_percent = float(match.group(1)) if match else None

        # -------------------------
        # Seeds Parsing
        # -------------------------
        seeds_raw = recomm_row.get(f"{prefix}Seeds", "")
        seed_list = []

        if isinstance(seeds_raw, str) and seeds_raw.strip():

            seeds_clean = seeds_raw.replace(
                "Top recommended seed varieties:", ""
            ).strip()

            parts = seeds_clean.split(") |")

            for part in parts:
                part = part.strip()
                if not part.endswith(")"):
                    part = part + ")"
                seed_list.append(part)

        # -------------------------
        # Yield Projection (from first seed)
        # -------------------------
        expected_without_fert = None
        expected_with_fert = None

        if seed_list:
            first_seed = seed_list[0]

            match_no = re.search(
                r"Expected w/o Fertiliser:\s*([\d\.\-\s]+t/Ha)",
                first_seed
            )

            match_yes = re.search(
                r"Expected w/ Fertiliser:\s*([\d\.\-\s]+t/Ha)",
                first_seed
            )

            if match_no:
                expected_without_fert = match_no.group(1).strip()

            if match_yes:
                expected_with_fert = match_yes.group(1).strip()

        # -------------------------
        # Risk & Confidence
        # -------------------------
        failure_pct = factors_row.get(f"{prefix}Overall_Failure_ward_pct")
        uncertainty = factors_row.get(f"{prefix}Overall_Failure_uncertainty")

        if failure_pct is None:
            risk_level = "Unknown"
        elif failure_pct > 50:
            risk_level = "High"
        elif failure_pct > 20:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        # Confidence Tier
        if uncertainty is None:
            confidence_tier = None
        elif uncertainty < 5:
            confidence_tier = 1
        elif uncertainty < 10:
            confidence_tier = 2
        elif uncertainty < 20:
            confidence_tier = 3
        else:
            confidence_tier = 4

        # -------------------------
        # Soil
        # -------------------------
        soil_values = {
            "stone_content": factors_row.get(f"{prefix}stone_content_ward_avg"),
            "bedrock_depth": factors_row.get(f"{prefix}bedrock_depth_ward_avg"),
            "texture_score": factors_row.get(f"{prefix}texture_score"),
        }

        # -------------------------
        # Final Response
        # -------------------------
        return {
            "ward": ward_name,
            "season": season,
            "seed_recommendation": {
                "suitability_percent": suitability_percent,
                "suitability_text": suitability_text,
                "overall_failure_probability_percent": failure_pct,
                "recommended_varieties": seed_list,
                "planting_window": recomm_row.get(f"{prefix}Planting_Window"),
                "yield_projection": {
                    "expected_without_fertiliser": expected_without_fert,
                    "expected_with_fertiliser": expected_with_fert
                }
            },
            "fertilizer": {
                "soil_values": soil_values,
                "recommended_fertiliser": recomm_row.get(f"{prefix}Fertiliser")
            },
            "advisory": {
                "risk_level": risk_level,
                "confidence_score_percent": uncertainty,
                "confidence_tier": confidence_tier,
                "risk_breakdown_percent": {
                    "cold": factors_row.get(f"{prefix}Cold_Risk_ward_pct"),
                    "heat": factors_row.get(f"{prefix}Heat_Risk_ward_pct"),
                    "drought": factors_row.get(f"{prefix}Drought_Risk_ward_pct")
                },
                "risk_warning_text": recomm_row.get(f"{prefix}Risk_Warnings")
            }
        }