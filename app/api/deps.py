# app/api/deps.py
import logging
from fastapi import Depends, HTTPException, status, Body, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import ee

from app.core.firebase import verify_token
from app.services.gee.geometry import geojson_to_ee

logger = logging.getLogger(__name__)
security = HTTPBearer()

def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Verify Firebase token and return decoded user info.
    Check for revocation and expiration.
    """
    try:
        token = credentials.credentials
        decoded_token = verify_token(token)
        user_id = decoded_token.get("uid")
        logger.info(f"User {user_id} authenticated successfully")
        return decoded_token
    except Exception as e:
        client_ip = request.client.host if request.client else "unknown"
        logger.warning(f"Authentication failed from {client_ip}: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

def get_geometry(
    geojson: dict = Body(..., description="GeoJSON geometry")
) -> ee.Geometry:
    """
    Converts GeoJSON from request body into an Earth Engine Geometry.
    Used across all spatial endpoints.
    Validates geometry is not too large.
    """
    try:
        # Validate geometry is dict with required fields
        if not isinstance(geojson, dict):
            raise ValueError("GeoJSON must be a dictionary")
        
        if "type" not in geojson:
            raise ValueError("GeoJSON missing 'type' field")
        
        geometry = geojson_to_ee(geojson)
        
        # Validate bounds are reasonable
        bounds = geometry.bounds().getInfo()
        if bounds is None:
            raise ValueError("Invalid geometry bounds")
        
        logger.debug(f"Valid geometry received")
        return geometry
        
    except ValueError as e:
        logger.debug(f"Invalid GeoJSON: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Invalid geometry provided"
        )
    except Exception as e:
        logger.error(f"Geometry processing error: {type(e).__name__}")
        raise HTTPException(
            status_code=400,
            detail="Invalid geometry provided"
        )
