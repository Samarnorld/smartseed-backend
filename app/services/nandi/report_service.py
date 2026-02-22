from .raster_engine import read_point_value, read_polygon_mean
import os

def generate_report(payload):

    season = payload["season"]

    suit_raster = f"Suit_Mean_{season}.tif"
    risk_raster = f"Risks_Mean_{season}.tif"

    if payload["type"] == "point":
        lat = payload["lat"]
        lon = payload["lon"]

        suitability = read_point_value(suit_raster, lat, lon)
        risk = read_point_value(risk_raster, lat, lon)

    elif payload["type"] == "polygon":
        geometry = payload["geometry"]

        suitability = read_polygon_mean(suit_raster, geometry)
        risk = read_polygon_mean(risk_raster, geometry)

    else:
        raise ValueError("Unsupported type")

    return {
        "suitability_score": suitability,
        "risk_score": risk
    }