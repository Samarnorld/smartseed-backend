# app/main.py
# libraries and modules import
from dotenv import load_dotenv
load_dotenv()   

import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
from slowapi.middleware import SlowAPIMiddleware
from app.core.limiter import limiter
from app.core.security import (
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
    ErrorLoggingMiddleware
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from app.api.endpoints import boundaries_router, gee_router
from app.api.endpoints.location import router as location_router
from app.api.endpoints.ndvi import router as ndvi_router
from app.api.endpoints.ndvi_tiles import router as ndvi_tiles_router
from app.api.endpoints.ndvi_climatology import router as ndvi_climatology_router
from app.api.endpoints.ndvi_anomaly import router as ndvi_anomaly_router
from app.api.endpoints.rainfall import router as rainfall_router
from app.api.endpoints.rainfall_tiles import router as rainfall_tiles_router
from app.api.endpoints.rainfall_monthly import router as rainfall_monthly_router
from app.api.endpoints.rainfall_anomaly import router as rainfall_anomaly_router
from app.api.endpoints.rainfall_climatology import router as rainfall_climatology_router
from app.api.endpoints.temperature import router as temperature_router
from app.api.endpoints.temperature_tiles import router as temperature_tiles_router
from app.api.endpoints.temperature_monthly import router as temperature_monthly_router
from app.api.endpoints.temperature_anomaly import router as temperature_anomaly_router
from app.api.endpoints.elevation import router as elevation_router
from app.api.endpoints.elevation_tiles import router as elevation_tiles_router
from app.api.endpoints.soil_analysis import router as soil_analysis_router
from app.api.endpoints.soil_tiles import router as soil_tiles_router
from app.api.endpoints.maize_suitability import router as maize_suitability_router
from app.api.endpoints.maize_timeseries import router as maize_timeseries_router
from app.api.endpoints.maize_suitability import router as maize_suitability_router
from app.api.endpoints.nandi_recommendations import router as nandi_recommendations_router
from app.api.endpoints.ussd import router as ussd_router
from app.api.endpoints.account_deletion import router as account_deletion_router
from app.core.gee_auth import init_gee

# Centralized limiter imported from app.core.limiter

# Import of future modules
# from app.db.session import get_db
# from app.api.endpoints import zones, recommendations

app = FastAPI(
    title="SmartSeed Zone Recommender API",
    description="Backend for climate-resilient seed recommendations",
    version="1.0.0"
)

# startup to initialize GEE
@app.on_event("startup")
def startup_event():
    logger.info("Starting up SmartSeed API...")
    init_gee()

# CORS middleware - Restrict to specific origins only
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://smartaseed.cliffordgeoconsult.com,"
    "http://localhost:5173,"
    "http://127.0.0.1:5173"
).split(",")

# Strip whitespace from each origin
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS]

logger.info(f"CORS allowed origins: {ALLOWED_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,  # Don't allow credentials for cross-origin
    allow_methods=["GET", "POST"],  # Only needed methods
    allow_headers=["authorization", "content-type", "accept"],  # Restrict headers
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# Add security middleware in order
app.add_middleware(ErrorLoggingMiddleware)  # Should be first to catch all errors
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)

# Rate limiting middleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

app.include_router(boundaries_router, prefix="/api")
app.include_router(location_router, prefix="/api")
app.include_router(gee_router, prefix="/api")
app.include_router(ndvi_router, prefix="/api")
app.include_router(ndvi_tiles_router, prefix="/api")
app.include_router(ndvi_climatology_router, prefix="/api")
app.include_router(ndvi_anomaly_router, prefix="/api")
app.include_router(rainfall_tiles_router, prefix="/api")
app.include_router(rainfall_router, prefix="/api")
app.include_router(rainfall_monthly_router, prefix="/api")
app.include_router(rainfall_anomaly_router, prefix="/api")
app.include_router(rainfall_climatology_router, prefix="/api")
app.include_router(temperature_tiles_router, prefix="/api")
app.include_router(temperature_router, prefix="/api")
app.include_router(temperature_monthly_router, prefix="/api")
app.include_router(temperature_anomaly_router, prefix="/api")
app.include_router(elevation_router, prefix="/api")
app.include_router(elevation_tiles_router, prefix="/api")
app.include_router(soil_analysis_router, prefix="/api")
app.include_router(soil_tiles_router, prefix="/api")
app.include_router(maize_suitability_router, prefix="/api")
app.include_router(maize_timeseries_router, prefix="/api")
app.include_router(nandi_recommendations_router, prefix="/api")
app.include_router(ussd_router)
app.include_router(account_deletion_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Welcome to the SmartSeed Zone Recommender API",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs"
    }

# Added one more blank line here to make two total
@app.get("/health")
async def health_check():
    """Essential endpoint for monitoring."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    