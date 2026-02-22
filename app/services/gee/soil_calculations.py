# app/services/gee/soil_calculations.py
def calculate_base_saturation(calcium, magnesium, potassium, cec):
    if cec is None or cec == 0:
        return None
    total_bases = 0
    if calcium:
        total_bases += calcium
    if magnesium:
        total_bases += magnesium
    if potassium:
        total_bases += potassium
    return (total_bases / cec) * 100