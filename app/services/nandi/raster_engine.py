import os
import rasterio
import numpy as np
from rasterio.mask import mask

BASE_PATH = os.path.join(
    os.getcwd(),
    "02_NandiSeedRecommender2",
    "Final_Outputs"
)

def _open_raster(name):
    return rasterio.open(os.path.join(BASE_PATH, name))

def read_point_value(raster_name, lat, lon):
    with _open_raster(raster_name) as src:
        row, col = src.index(lon, lat)
        return float(src.read(1)[row, col])

def read_polygon_mean(raster_name, geometry):
    with _open_raster(raster_name) as src:
        out_image, _ = mask(src, [geometry], crop=True)
        data = out_image[0]
        data = data[data != src.nodata]
        return float(np.mean(data))