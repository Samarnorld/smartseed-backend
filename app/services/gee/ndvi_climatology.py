# app/services/gee/ndvi_climatology.py
import ee
from datetime import datetime
from app.services.gee.ndvi import get_ndvi_timeseries

def get_ndvi_climatology(geometry, baseline_years: int = 5):

    current_year = datetime.utcnow().year
    start_year = current_year - baseline_years
    end_year = current_year - 1

    data = get_ndvi_timeseries(geometry, start_year, end_year)

    return {
        "baseline_period": f"{start_year}-{end_year}",
        "years_used": baseline_years,
        "monthly_climatology": data
    }