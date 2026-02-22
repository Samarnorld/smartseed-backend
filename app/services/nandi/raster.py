#  app/services/nandi/raster.py
import os
import numpy as np
import rasterio
from rasterio.mask import mask
from shapely.geometry import box, mapping

BASE_PATH = "data/02_NandiSeedRecommender2/Final_Outputs"


def safe_float(value):
    if value is None:
        return None
    if np.isnan(value) or np.isinf(value):
        return None
    return float(value)


def zonal_mean(tif_path, geometry):

    with rasterio.open(tif_path) as src:

        # Clip geometry to raster bounds
        raster_bbox = box(*src.bounds)
        clipped_geom = geometry.intersection(raster_bbox)

        if clipped_geom.is_empty:
            return None

        geom = [mapping(clipped_geom)]

        out_image, _ = mask(src, geom, crop=True)
        data = out_image[0]

        if src.nodata is not None:
            data = data[data != src.nodata]

        if data.size == 0:
            return None

        value = np.mean(data)
        return safe_float(value)


def suitability(geometry, season="LongRains"):
    mean_path = os.path.join(BASE_PATH, f"Suit_Mean_{season}.tif")
    std_path = os.path.join(BASE_PATH, f"Suit_Std_{season}.tif")

    mean_val = zonal_mean(mean_path, geometry)
    std_val = zonal_mean(std_path, geometry)

    return {
        "mean_percent": round(mean_val * 100, 2) if mean_val is not None else None,
        "uncertainty": round(std_val, 4) if std_val is not None else None,
    }


def soil_profile(geometry, season="LongRains"):
    factor_path = f"{BASE_PATH}/Factors_{season}"

    def f(name):
        return zonal_mean(f"{factor_path}/{name}_mean.tif", geometry)

    def r(v):
        return round(v, 2) if v is not None else None

    return {
        "ph": r(f("ph")),
        "organic_carbon": r(f("organic_carbon")),
        "nitrogen": r(f("total_nitrogen")),
        "phosphorus": r(f("phosphorus")),
        "potassium": r(f("potassium")),
    }


def risks(geometry, season="LongRains"):
    path = os.path.join(BASE_PATH, f"Risks_Mean_{season}.tif")

    with rasterio.open(path) as src:

        raster_bbox = box(*src.bounds)
        clipped_geom = geometry.intersection(raster_bbox)

        if clipped_geom.is_empty:
            return {
                "cold": None,
                "heat": None,
                "drought": None,
                "flood": None,
                "failure": None,
            }

        geom = [mapping(clipped_geom)]
        out_image, _ = mask(src, geom, crop=True)
        bands = out_image

        labels = ["cold", "heat", "drought", "flood", "failure"]
        result = {}

        for i, label in enumerate(labels):
            band = bands[i]

            if src.nodata is not None:
                band = band[band != src.nodata]

            if band.size == 0:
                result[label] = None
                continue

            value = np.mean(band)
            value = safe_float(value)

            result[label] = round(value * 100, 2) if value is not None else None

        return result


def confidence(geometry, season="LongRains"):
    path = os.path.join(BASE_PATH, f"Conf_Tier_{season}.tif")
    value = zonal_mean(path, geometry)
    return round(value, 2) if value is not None else None