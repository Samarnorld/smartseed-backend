# app/services/gee/soil_interpretation.py
def classify_ph(value):
    if value is None:
        return "No data"
    if value < 5.5:
        return "Strongly acidic"
    elif value < 6.0:
        return "Moderately acidic"
    elif value <= 7.5:
        return "Optimal"
    else:
        return "Alkaline"