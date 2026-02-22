# app/services/nandi/config.py
import os

BASE_PATH = os.getenv("NANDI_DATA_PATH", "02_NandiSeedRecommender2")
FINAL_OUTPUTS = os.path.join(BASE_PATH, "Final_Outputs")
SEED_DATA = os.path.join(BASE_PATH, "Seed_Data", "KenyaSeedWebScrape.xlsx")


def suitability_paths(season: str):
    if season == "LongRains":
        return (
            os.path.join(FINAL_OUTPUTS, "Suit_Mean_LongRains.tif"),
            os.path.join(FINAL_OUTPUTS, "Suit_Std_LongRains.tif"),
            os.path.join(FINAL_OUTPUTS, "Factors_LongRains", "prob_overall_fail_mean.tif"),
            os.path.join(FINAL_OUTPUTS, "Conf_Tier_LongRains.tif"),
        )
    else:
        return (
            os.path.join(FINAL_OUTPUTS, "Suit_Mean_ShortRains.tif"),
            os.path.join(FINAL_OUTPUTS, "Suit_Std_ShortRains.tif"),
            os.path.join(FINAL_OUTPUTS, "Factors_ShortRains", "prob_overall_fail_mean.tif"),
            os.path.join(FINAL_OUTPUTS, "Conf_Tier_ShortRains.tif"),
        )


def risk_factor_paths(season: str):
    folder = "Factors_LongRains" if season == "LongRains" else "Factors_ShortRains"
    base = os.path.join(FINAL_OUTPUTS, folder)

    return {
        "heat": os.path.join(base, "prob_heat_mean.tif"),
        "drought": os.path.join(base, "prob_drought_mean.tif"),
        "flood": os.path.join(base, "prob_flood_mean.tif"),
        "cold": os.path.join(base, "prob_cold_mean.tif"),
    }


def soil_paths(season: str):
    folder = "Raw_Values_LongRains" if season == "LongRains" else "Raw_Values_ShortRains"
    base = os.path.join(FINAL_OUTPUTS, folder)

    return {
        "N": os.path.join(base, "total_nitrogen_raw.tif"),
        "P": os.path.join(base, "phosphorus_raw.tif"),
        "K": os.path.join(base, "potassium_raw.tif"),
        "pH": os.path.join(base, "ph_raw.tif"),
        "organic_carbon": os.path.join(base, "organic_carbon_raw.tif"),
        "magnesium": os.path.join(base, "magnesium_raw.tif"),
        "zinc": os.path.join(base, "zinc_raw.tif"),
        "bedrock_depth": os.path.join(base, "bedrock_depth_raw.tif"),
        "stone_content": os.path.join(base, "stone_content_raw.tif"),
        "texture": os.path.join(base, "texture_raw.tif"),
    }