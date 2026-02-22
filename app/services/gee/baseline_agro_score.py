# app/services/gee/baseline_agro_score.py
import ee
from app.services.gee.soil_config import ISDA_BASE, VALID_DEPTHS
def compute_baseline_score(
    geometry: ee.Geometry,
    depth: str = "0-20cm"
) -> float:

    if depth not in VALID_DEPTHS:
        raise ValueError("Invalid soil depth")

    band = VALID_DEPTHS[depth]

    # Soil layers
    ph = ee.Image(f"{ISDA_BASE}/ph").select(band).multiply(0.1)
    oc = ee.Image(f"{ISDA_BASE}/carbon_organic").select(band).multiply(0.1)
    cec = ee.Image(f"{ISDA_BASE}/cation_exchange_capacity").select(band)

    # Centered agronomic scoring
    # Ideal maize pH ≈ 6.2
    ph_score = ee.Image(1).subtract(
        ph.subtract(6.2).abs().divide(1.5)
    ).clamp(0, 1)

    # Organic Carbon ideal up to 3%
    oc_score = oc.divide(3).clamp(0, 1)

    # CEC moderate-high ideal (up to 35)
    cec_score = cec.divide(35).clamp(0, 1)

    baseline = (
        ph_score.multiply(0.4)
        .add(oc_score.multiply(0.3))
        .add(cec_score.multiply(0.3))
    ).multiply(100)

    result = baseline.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=250,
        maxPixels=1e13
    ).getInfo()

    return list(result.values())[0]