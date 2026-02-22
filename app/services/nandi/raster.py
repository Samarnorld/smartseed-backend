# app/services/nandi/raster.py

import os
import numpy as np
import rasterio
from rasterio.mask import mask

BASE_PATH = "data/02_NandiSeedRecommender2/Final_Outputs"


def zonal_mean(tif_path, geometry):
    with rasterio.open(tif_path) as src:
        out_image, _ = mask(src, [geometry], crop=True)
        data = out_image[0]
        data = data[data != src.nodata]
        if data.size == 0:
            return None
        return float(np.mean(data))


def suitability(geometry, season="LongRains"):
    mean_path = os.path.join(BASE_PATH, f"Suit_Mean_{season}.tif")
    std_path = os.path.join(BASE_PATH, f"Suit_Std_{season}.tif")

    return {
        "mean_percent": round(zonal_mean(mean_path, geometry) * 100, 2),
        "uncertainty": round(zonal_mean(std_path, geometry), 4),
    }


def soil_profile(geometry, season="LongRains"):
    factor_path = f"{BASE_PATH}/Factors_{season}"

    def f(name):
        return zonal_mean(f"{factor_path}/{name}_mean.tif", geometry)

    return {
        "ph": round(f("ph"), 2),
        "organic_carbon": round(f("organic_carbon"), 2),
        "nitrogen": round(f("total_nitrogen"), 2),
        "phosphorus": round(f("phosphorus"), 2),
        "potassium": round(f("potassium"), 2),
    }


def risks(geometry, season="LongRains"):
    path = os.path.join(BASE_PATH, f"Risks_Mean_{season}.tif")

    with rasterio.open(path) as src:
        out_image, _ = mask(src, [geometry], crop=True)
        bands = out_image

    labels = ["cold", "heat", "drought", "flood", "failure"]

    result = {}
    for i, label in enumerate(labels):
        band = bands[i]
        band = band[band != src.nodata]
        result[label] = round(float(np.mean(band) * 100), 2)

    return result


def confidence(geometry, season="LongRains"):
    path = os.path.join(BASE_PATH, f"Conf_Tier_{season}.tif")
    value = zonal_mean(path, geometry)
    return round(value, 2)