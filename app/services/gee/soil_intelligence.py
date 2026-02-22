# app/services/gee/soil_intelligence.py
from app.services.gee.soil_calculations import calculate_base_saturation
from app.services.gee.soil_interpretation import classify_ph

def build_soil_intelligence(raw):

    ph = raw["ph"]["mean"]
    cec = raw["cec"]["mean"]

    ca = raw["calcium"]["mean"]
    mg = raw["magnesium"]["mean"]
    k = raw["potassium"]["mean"]

    clay = raw["clay"]["mean"]
    sand = raw["sand"]["mean"]
    silt = raw["silt"]["mean"]

    base_sat = calculate_base_saturation(ca, mg, k, cec)

    return {
        "ph": {
            "value": ph,
            "status": classify_ph(ph),
        },

        "texture_percent": {
            "clay": clay,
            "sand": sand,
            "silt": silt,
        },

        "base_saturation_percent": base_sat,

        "cec_cmol_per_kg": cec,

        "exchangeable_bases_cmol_per_kg": {
            "calcium": ca,
            "magnesium": mg,
            "potassium": k,
        },

        "organic_carbon_percent": raw["organic_carbon"]["mean"],

        "bulk_density_g_cm3": raw["bulk_density"]["mean"],
    }