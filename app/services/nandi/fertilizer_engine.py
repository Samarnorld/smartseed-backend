# app/services/nandi/fertilizer_engine.py
from typing import Dict
from .config import soil_paths
from .raster_sampling import sample_raster
class NandiFertilizerEngine:

    @staticmethod
    def recommend(lon: float, lat: float, season: str) -> Dict:

        paths = soil_paths(season)

        N = sample_raster(paths["N"], lon, lat)
        P = sample_raster(paths["P"], lon, lat)
        K = sample_raster(paths["K"], lon, lat)
        pH = sample_raster(paths["pH"], lon, lat)

        advice = []

        if N is not None and N < 0.2:
            advice.append("Apply Nitrogen fertilizer (CAN/Urea)")
        if P is not None and P < 15:
            advice.append("Apply Phosphorus fertilizer (DAP/TSP)")
        if K is not None and K < 100:
            advice.append("Apply Potassium fertilizer (MOP)")
        if pH is not None and pH < 5.5:
            advice.append("Apply Agricultural Lime")

        return {
            "soil_values": {
                "N": N,
                "P": P,
                "K": K,
                "pH": pH
            },
            "fertilizer_recommendations": advice
        }