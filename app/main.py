# Import necessary libraries and modules
from dotenv import load_dotenv
load_dotenv()   

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

from app.api.endpoints import boundaries_router

# Import your future modules here. For now, we'll create placeholders.
# from app.db.session import get_db
# from app.api.endpoints import zones, recommendations

app = FastAPI(
    title="SmartSeed Zone Recommender API",
    description="Backend for climate-resilient seed recommendations",
    version="1.0.0"
)

# Add CORS middleware (allows frontend to talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(boundaries_router, prefix="/api")

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
    