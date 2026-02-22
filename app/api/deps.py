# app/api/deps.py
from fastapi import Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import ee

from app.core.firebase import verify_token
from app.services.gee.geometry import geojson_to_ee

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        decoded_token = verify_token(token)
        return decoded_token
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase token",
        )

def get_geometry(
    geojson: dict = Body(..., description="GeoJSON geometry")
) -> ee.Geometry:
    """
    Converts GeoJSON from request body into an Earth Engine Geometry.
    Used across all spatial endpoints.
    """
    try:
        return geojson_to_ee(geojson)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid GeoJSON provided: {str(e)}"
        )
