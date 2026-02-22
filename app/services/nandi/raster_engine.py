# app/services/nandi/raster_engine.py

import rasterio
import os
from typing import Dict

BASE_PATH = "data/02_NandiSeedRecommender2/Final_Outputs"


def _read_single_pixel(tif_path: str, lat: float, lon: float):
    if not os.path.exists(tif_path):
        raise FileNotFoundError(f"{tif_path} not found")

    with rasterio.open(tif_path) as src:
        row, col = src.index(lon, lat)
        value = src.read(1)[row, col]

    return float(value)


def get_suitability(lat: float, lon: float, season: str = "LongRains") -> Dict:
    mean_path = os.path.join(BASE_PATH, f"Suit_Mean_{season}.tif")
    std_path = os.path.join(BASE_PATH, f"Suit_Std_{season}.tif")

    suitability = _read_single_pixel(mean_path, lat, lon)
    uncertainty = _read_single_pixel(std_path, lat, lon)

    return {
        "suitability_percent": round(suitability * 100, 2),
        "uncertainty": round(uncertainty, 4),
        "season": season
    }


def get_risks(lat: float, lon: float, season: str = "LongRains") -> Dict:
    mean_path = os.path.join(BASE_PATH, f"Risks_Mean_{season}.tif")
    std_path = os.path.join(BASE_PATH, f"Risks_Std_{season}.tif")

    if not os.path.exists(mean_path):
        raise FileNotFoundError("Risk raster not found")

    with rasterio.open(mean_path) as mean_src:
        row, col = mean_src.index(lon, lat)
        risk_means = mean_src.read(window=((row, row+1), (col, col+1)))[:, 0, 0]

    with rasterio.open(std_path) as std_src:
        row, col = std_src.index(lon, lat)
        risk_stds = std_src.read(window=((row, row+1), (col, col+1)))[:, 0, 0]

    labels = [
        "cold_risk",
        "heat_risk",
        "drought_risk",
        "flood_risk",
        "overall_failure"
    ]

    results = {}

    for i, label in enumerate(labels):
        results[label] = {
            "probability_percent": round(risk_means[i] * 100, 2),
            "uncertainty": round(risk_stds[i], 4)
        }

    return results