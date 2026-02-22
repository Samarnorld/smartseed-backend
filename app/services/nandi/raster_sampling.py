# app/services/nandi/raster_sampling.py
import rasterio
from typing import Optional

def sample_raster(raster_path: str, lon: float, lat: float) -> Optional[float]:
    """
    Safely sample a raster value at lon/lat.
    Returns None if outside bounds or nodata.
    """
    try:
        with rasterio.open(raster_path) as src:
            bounds = src.bounds

            if not (bounds.left <= lon <= bounds.right and
                    bounds.bottom <= lat <= bounds.top):
                return None

            row, col = src.index(lon, lat)
            value = src.read(1)[row, col]

            if value == src.nodata:
                return None

            return float(value)

    except Exception:
        return None