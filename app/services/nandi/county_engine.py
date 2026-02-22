# app/services/nandi/county_engine.py
import json
import os
import re
import pandas as pd
from typing import Dict
from .config import FINAL_OUTPUTS, BASE_PATH


COUNTY_PATH = os.path.join(FINAL_OUTPUTS, "County_Averages.json")

WARD_RECOMM_PATH = os.path.join(
    BASE_PATH,
    "WardAggregatedData",
    "Nandi_Ward_Recommendations.csv"
)


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

        # -------------------------
        # Convert Scores to %
        # -------------------------
        mean_suitability = scores.get("temp")
        failure = scores.get("prob_overall_fail")

        suitability_percent = round(mean_suitability * 100, 2) if mean_suitability else None
        failure_percent = round(failure * 100, 2) if failure else None

        # -------------------------
        # Suitability Class
        # -------------------------
        if suitability_percent is None:
            suitability_class = "Unknown"
        elif suitability_percent >= 80:
            suitability_class = "Highly Suitable"
        elif suitability_percent >= 60:
            suitability_class = "Moderately Suitable"
        else:
            suitability_class = "Marginal"

        # -------------------------
        # Risk Level
        # -------------------------
        if failure_percent is None:
            risk_level = "Unknown"
        elif failure_percent > 50:
            risk_level = "High"
        elif failure_percent > 20:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        # -------------------------
        # Dominant Limiting Factor
        # -------------------------
        stress_dict = {
            "heat": scores.get("prob_heat"),
            "drought": scores.get("prob_drought"),
            "flood": scores.get("prob_flood"),
            "cold": scores.get("prob_cold")
        }

        dominant_factor = max(
            stress_dict,
            key=lambda k: stress_dict.get(k) or 0
        )

        # -------------------------
        # County Seed Recommendation
        # Logic: choose most frequently recommended top seed across wards
        # -------------------------
        top_seed = None
        yield_without = None
        yield_with = None

        if os.path.exists(WARD_RECOMM_PATH):

            df = pd.read_csv(WARD_RECOMM_PATH)

            prefix = "LR_" if season == "LongRains" else "SR_"

            seed_counts = {}

            for seed_string in df[f"{prefix}Seeds"].dropna():

                if "Top recommended seed varieties:" in seed_string:
                    seed_string = seed_string.replace(
                        "Top recommended seed varieties:", ""
                    )

                parts = seed_string.split(") |")

                if parts:
                    first_seed = parts[0]
                    seed_name = first_seed.split("(")[0].strip()

                    seed_counts[seed_name] = seed_counts.get(seed_name, 0) + 1

                    # Extract yield from first occurrence
                    if not yield_with:
                        match_yes = re.search(
                            r"Expected w/ Fertiliser:\s*([\d\.\-\s]+t/Ha)",
                            first_seed
                        )
                        if match_yes:
                            yield_with = match_yes.group(1).strip()

                    if not yield_without:
                        match_no = re.search(
                            r"Expected w/o Fertiliser:\s*([\d\.\-\s]+t/Ha)",
                            first_seed
                        )
                        if match_no:
                            yield_without = match_no.group(1).strip()

            if seed_counts:
                top_seed = max(seed_counts, key=seed_counts.get)

        # -------------------------
        # County Bulletin Summary
        # -------------------------
        season_readable = "Long Rains season" if season == "LongRains" else "Short Rains season"
        county_summary = (
            f"For the upcoming {season_readable}, maize production conditions "
            f"across Nandi County are assessed as {suitability_class.lower()}. "
        )

        if suitability_percent:
            county_summary += (
                f"Average land suitability stands at {suitability_percent}%, "
            )

        if failure_percent:
            county_summary += (
                f"with a projected seasonal production risk of {failure_percent}%. "
            )

        county_summary += (
            f"The primary climatic constraint this season is {dominant_factor}. "
        )

        if top_seed:
            county_summary += (
                f"The most widely recommended maize variety across wards is {top_seed}. "
            )

        if yield_with:
            county_summary += (
                f"Under proper fertiliser management, expected yields range between "
                f"{yield_with}. "
            )
        # -------------------------
        # Final Response
        # -------------------------
        return {
            "county": "Nandi",
            "season": season,
            "seed_recommendation": {
                "mean_suitability_percent": suitability_percent,
                "suitability_class": suitability_class,
                "overall_failure_probability_percent": failure_percent,
                "recommended_county_seed": top_seed,
                "yield_projection": {
                    "expected_without_fertiliser": yield_without,
                    "expected_with_fertiliser": yield_with
                }
            },
            "fertilizer": {
                "soil_values": raw
            },
            "advisory": {
                "risk_level": risk_level,
                "dominant_limiting_factor": dominant_factor,
                "county_summary": county_summary
            }
        }