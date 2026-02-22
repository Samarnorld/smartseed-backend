# app/services/nandi/engine.py

from app.services.nandi.geometry import (
    from_point,
    from_polygon,
    from_ward,
    from_county,
)

from app.services.nandi.raster import (
    suitability,
    soil_profile,
    risks,
    confidence,
)

def recommend_seed(soil, risk, suit):

    if suit["mean_percent"] is None:
        return ["Data unavailable"]

    if suit["mean_percent"] < 40:
        return ["Drought Resistant Hybrid"]

    if risk["drought"] is not None and risk["drought"] > 30:
        return ["DH04", "KDV4"]

    if soil["ph"] is not None and soil["ph"] < 5.5:
        return ["Acid Tolerant Hybrid"]

    return ["H6213", "WH505"]

def recommend_fertilizer(soil):
    rec = []
    if soil["phosphorus"] is not None and soil["phosphorus"] < 15:
        rec.append("DAP at planting")
    if soil["nitrogen"] is not None and soil["nitrogen"] < 0.2:
        rec.append("CAN top dressing")
    if soil["ph"] is not None and soil["ph"] < 5.5:
        rec.append("Apply agricultural lime")
    return rec

def analyze(request: dict):

    season = request.get("season", "LongRains")

    if "ward" in request:
        geometry = from_ward(request["ward"])
    elif "polygon" in request:
        geometry = from_polygon(request["polygon"])
    elif "lat" in request:
        geometry = from_point(request["lat"], request["lon"])
    else:
        geometry = from_county()

    suit = suitability(geometry, season)
    soil = soil_profile(geometry, season)
    risk = risks(geometry, season)
    conf = confidence(geometry, season)

    return {
        "season": season,
        "suitability": suit,
        "soil": soil,
        "risks": risk,
        "confidence_tier": conf,
        "recommended_seeds": recommend_seed(soil, risk, suit),
        "fertilizer_plan": recommend_fertilizer(soil),
    }