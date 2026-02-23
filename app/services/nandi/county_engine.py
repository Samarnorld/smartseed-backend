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

        # Load County JSON
        if not os.path.exists(COUNTY_PATH):
            return {"error": "County averages file not found"}

        with open(COUNTY_PATH, "r") as f:
            data = json.load(f)

        if season not in data:
            return {"error": "Season not found"}

        season_data = data[season]
        scores = season_data.get("scores", {})
        raw = season_data.get("raw", {})

        # Convert Scores to %
        mean_suitability = scores.get("temp")
        failure = scores.get("prob_overall_fail")

        suitability_percent = (
            round(mean_suitability * 100, 2)
            if mean_suitability is not None
            else None
        )

        failure_percent = (
            round(failure * 100, 2)
            if failure is not None
            else None
        )

        # Suitability Class
        if suitability_percent is None:
            suitability_class = "Unknown"
        elif suitability_percent >= 80:
            suitability_class = "Highly Suitable"
        elif suitability_percent >= 60:
            suitability_class = "Moderately Suitable"
        else:
            suitability_class = "Marginal"

        # Risk Classification
        if failure_percent is None:
            risk_level = "Unknown"
        elif failure_percent > 50:
            risk_level = "High"
        elif failure_percent > 20:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        # Dominant Limiting Factor
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

        # County Seed Recommendation
        top_seed = None
        yield_without_values = []
        yield_with_values = []

        if os.path.exists(WARD_RECOMM_PATH):

            df = pd.read_csv(WARD_RECOMM_PATH)
            prefix = "LR_" if season == "LongRains" else "SR_"

            seed_counts = {}

            # Count most frequent top seed
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

            if seed_counts:
                top_seed = max(seed_counts, key=seed_counts.get)

                # Now compute average yields ONLY for that seed
                for seed_string in df[f"{prefix}Seeds"].dropna():

                    if top_seed in seed_string:

                        match_no = re.search(
                            r"Expected w/o Fertiliser:\s*([\d\.]+)\s*-\s*([\d\.]+)",
                            seed_string
                        )

                        match_yes = re.search(
                            r"Expected w/ Fertiliser:\s*([\d\.]+)\s*-\s*([\d\.]+)",
                            seed_string
                        )

                        if match_no:
                            low = float(match_no.group(1))
                            high = float(match_no.group(2))
                            yield_without_values.append((low, high))

                        if match_yes:
                            low = float(match_yes.group(1))
                            high = float(match_yes.group(2))
                            yield_with_values.append((low, high))

        # Compute averaged yield ranges
        yield_without = None
        yield_with = None

        if yield_without_values:
            avg_low = sum(v[0] for v in yield_without_values) / len(yield_without_values)
            avg_high = sum(v[1] for v in yield_without_values) / len(yield_without_values)
            yield_without = f"{round(avg_low, 2)} - {round(avg_high, 2)} t/Ha"

        if yield_with_values:
            avg_low = sum(v[0] for v in yield_with_values) / len(yield_with_values)
            avg_high = sum(v[1] for v in yield_with_values) / len(yield_with_values)
            yield_with = f"{round(avg_low, 2)} - {round(avg_high, 2)} t/Ha"

        # Refined County Bulletin Summary
        season_readable = (
            "Long Rains season"
            if season == "LongRains"
            else "Short Rains season"
        )

        county_summary = (
            f"For the upcoming {season_readable}, maize production conditions "
            f"across Nandi County are expected to be {suitability_class.lower()}. "
        )

        if suitability_percent is not None:
            county_summary += (
                f"Average land suitability is estimated at {suitability_percent}%, "
            )

        if failure_percent is not None:
            county_summary += (
                f"with a projected seasonal production risk of {failure_percent}%. "
            )

        county_summary += (
            f"Drought is identified as the primary climatic constraint this season. "
        )

        if top_seed:
            county_summary += (
                f"{top_seed} stands out as the most consistently recommended "
                f"maize variety across wards. "
            )

        if yield_with:
            county_summary += (
                f"With appropriate fertiliser management, expected yields "
                f"range between {yield_with}."
            )
        # Final Response
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