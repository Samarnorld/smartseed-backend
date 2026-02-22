import json
import os

def load_geojson(path):
    with open(path) as f:
        return json.load(f)