# libraries and modules import
from dotenv import load_dotenv
load_dotenv()   

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

from app.api.endpoints import boundaries_router, gee_router
from app.api.endpoints.rainfall import router as rainfall_router
from app.api.endpoints.rainfall_tiles import router as rainfall_tiles_router
from app.api.endpoints.rainfall_monthly import router as rainfall_monthly_router
from app.api.endpoints.rainfall_anomaly import router as rainfall_anomaly_router
from app.api.endpoints.temperature import router as temperature_router
from app.api.endpoints.temperature_tiles import router as temperature_tiles_router
from app.api.endpoints.temperature_monthly import router as temperature_monthly_router
from app.api.endpoints.temperature_anomaly import router as temperature_anomaly_router
from app.api.endpoints.elevation import router as elevation_router
from app.api.endpoints.elevation_tiles import router as elevation_tiles_router
from app.api.endpoints.ndvi import router as ndvi_router
from app.api.endpoints.soil import router as soil_router
from app.core.gee_auth import init_gee

# Import of future modules
# from app.db.session import get_db
# from app.api.endpoints import zones, recommendations

app = FastAPI(
    title="SmartSeed Zone Recommender API",
    description="Backend for climate-resilient seed recommendations",
    version="1.0.0"
)

# startup event to initialize GEE
@app.on_event("startup")
def startup_event():
    init_gee()

# CORS middleware (allows frontend to talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(boundaries_router, prefix="/api")
app.include_router(gee_router, prefix="/api")
app.include_router(rainfall_tiles_router, prefix="/api")
app.include_router(rainfall_router, prefix="/api")
app.include_router(rainfall_monthly_router, prefix="/api")
app.include_router(rainfall_anomaly_router, prefix="/api")
app.include_router(temperature_tiles_router, prefix="/api")
app.include_router(temperature_router, prefix="/api")
app.include_router(temperature_monthly_router, prefix="/api")
app.include_router(temperature_anomaly_router, prefix="/api")
app.include_router(elevation_router, prefix="/api")
app.include_router(elevation_tiles_router, prefix="/api")
app.include_router(ndvi_router, prefix="/api")
app.include_router(soil_router, prefix="/api")

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
    