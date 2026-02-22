# app/services/gee/seasonal_performance.py
from app.services.gee.rainfall_anomaly import get_seasonal_anomaly as get_rain_anomaly
from app.services.gee.temperature_anomaly import get_temperature_seasonal_anomaly as get_temp_anomaly
from app.services.gee.ndvi_anomaly import get_seasonal_anomaly as get_ndvi_anomaly

# Kenya rainfall mapping
RAIN_SEASON_MAP = {
    "MAM": "long_rains",
    "SON": "short_rains",
    "JJA": "short_rains",
    "DJF": "long_rains"
}

def compute_seasonal_performance(geometry, year: int, season: str):

    rain_season = RAIN_SEASON_MAP.get(season, season)

    rain = get_rain_anomaly(geometry, year, rain_season)
    temp = get_temp_anomaly(geometry, season, year)
    ndvi = get_ndvi_anomaly(geometry, year, season)

    rain_anom = rain.get("anomaly_percent", 0)
    temp_anom = temp.get("mean_temp_anomaly_c", 0)
    ndvi_anom = ndvi.get("anomaly_percent", 0)

    # Rainfall stress curve 
    if rain_anom < -30:
        rain_factor = 0.7
    elif rain_anom < -10:
        rain_factor = 0.85
    elif rain_anom <= 20:
        rain_factor = 1.0
    elif rain_anom <= 40:
        rain_factor = 0.95
    else:
        rain_factor = 0.85

    # Temperature stress curve 
    if abs(temp_anom) < 1:
        temp_factor = 1.0
    elif abs(temp_anom) < 2:
        temp_factor = 0.9
    elif abs(temp_anom) < 3:
        temp_factor = 0.8
    else:
        temp_factor = 0.65

    # NDVI as validation signal
    ndvi_factor = 1 + (ndvi_anom / 100)

    spi = (
        0.4 * rain_factor +
        0.4 * temp_factor +
        0.2 * ndvi_factor
    )

    spi = max(0.6, min(1.2, spi))

    return {
        "spi": round(spi, 3),
        "rain_anomaly_percent": rain_anom,
        "temperature_anomaly_c": temp_anom,
        "ndvi_anomaly_percent": ndvi_anom
    }