HYBRIDS = [
    {"name": "DK8031", "rain_opt": (700, 1100), "ph_opt": (5.5, 6.8)},
    {"name": "H6213", "rain_opt": (600, 900), "ph_opt": (5.0, 6.5)},
    {"name": "SC Duma 43", "rain_opt": (500, 800), "ph_opt": (5.0, 7.0)},
]

def rank_hybrids(mean_rainfall, ph_value):

    results = []

    for hybrid in HYBRIDS:
        rain_score = (
            1 if hybrid["rain_opt"][0] <= mean_rainfall <= hybrid["rain_opt"][1]
            else 0.7
        )

        ph_score = (
            1 if hybrid["ph_opt"][0] <= ph_value <= hybrid["ph_opt"][1]
            else 0.8
        )

        score = (rain_score * 0.6 + ph_score * 0.4) * 100

        results.append({
            "hybrid": hybrid["name"],
            "score": round(score, 2)
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)