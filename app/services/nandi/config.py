# app/services/nandi/config.py
import os

# Base path (set this in .env in VPS)
# Example in .env:
# NANDI_DATA_PATH=/home/geoconsult/02_NandiSeedRecommender2

BASE_PATH = os.getenv("NANDI_DATA_PATH", "02_NandiSeedRecommender2")

FINAL_OUTPUTS = os.path.join(BASE_PATH, "Final_Outputs")
SEED_DATA = os.path.join(BASE_PATH, "Seed_Data", "KenyaSeedWebScrape.xlsx")


def suitability_paths(season: str):
    if season == "LongRains":
        return (
            os.path.join(FINAL_OUTPUTS, "Suit_Mean_LongRains.tif"),
            os.path.join(FINAL_OUTPUTS, "Suit_Std_LongRains.tif"),
            os.path.join(FINAL_OUTPUTS, "FailureProbability_LongRains.tif"),
        )
    else:
        return (
            os.path.join(FINAL_OUTPUTS, "Suit_Mean_ShortRains.tif"),
            os.path.join(FINAL_OUTPUTS, "Suit_Std_ShortRains.tif"),
            os.path.join(FINAL_OUTPUTS, "FailureProbability_ShortRains.tif"),
        )


def soil_paths(season: str):
    folder = "Raw_Values_LongRains" if season == "LongRains" else "Raw_Values_ShortRains"
    base = os.path.join(FINAL_OUTPUTS, folder)

    return {
        "N": os.path.join(base, "total_nitrogen_raw.tif"),
        "P": os.path.join(base, "phosphorus_raw.tif"),
        "K": os.path.join(base, "potassium_raw.tif"),
        "pH": os.path.join(base, "ph_raw.tif"),
    }