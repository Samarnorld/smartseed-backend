# app/services/nandi/fertilizer_engine.py
from typing import Dict
from .config import soil_paths
from .raster_sampling import sample_raster


class NandiFertilizerEngine:

    @staticmethod
    def recommend(lon: float, lat: float, season: str) -> Dict:

        paths = soil_paths(season)

        values = {
            key: sample_raster(path, lon, lat)
            for key, path in paths.items()
        }

        advice = []

        N = values["N"]
        P = values["P"]
        K = values["K"]
        pH = values["pH"]
        OC = values["organic_carbon"]
        Mg = values["magnesium"]
        Zn = values["zinc"]
        depth = values["bedrock_depth"]
        stones = values["stone_content"]

        if N is not None and N < 0.2:
            advice.append("Apply Nitrogen fertilizer (CAN/Urea)")

        if P is not None and P < 15:
            advice.append("Apply Phosphorus fertilizer (DAP/TSP)")

        if K is not None and K < 100:
            advice.append("Apply Potassium fertilizer (MOP)")

        if pH is not None and pH < 5.5:
            advice.append("Apply Agricultural Lime")

        if OC is not None and OC < 1.5:
            advice.append("Incorporate organic matter or compost")

        if Zn is not None and Zn < 1:
            advice.append("Apply Zinc micronutrient")

        if Mg is not None and Mg < 0.5:
            advice.append("Apply Magnesium supplement")

        if depth is not None and depth < 50:
            advice.append("Shallow soil depth – avoid deep-rooted varieties")

        if stones is not None and stones > 30:
            advice.append("High stone content – consider soil preparation")

        return {
            "soil_values": values,
            "fertilizer_recommendations": advice
        }