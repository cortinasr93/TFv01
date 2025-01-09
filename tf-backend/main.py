from fastapi import FastAPI, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from api.onboarding.services import OnboardingService
from core.database import engine, get_db
from core.models import detection, publisher, Base
from api.access_tokens import router as token_router
from api.detection import router as detection_router
from api.dashboard import router as dashboard_router
from api.onboarding import router as onboarding_router
from api.auth import router as auth_router
#from api.payments import router as payments_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="TrainFair Bot Detection System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
detection.Base.metadata.create_all(bind=engine)
publisher.Base.metadata.create_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(detection_router)
app.include_router(dashboard_router)
app.include_router(onboarding_router)
app.include_router(auth_router)
app.include_router(token_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "TrainFair Bot Detection System",
        "status": "running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)