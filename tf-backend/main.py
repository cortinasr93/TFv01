# tf-backend/main.py

from fastapi import FastAPI, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from api.onboarding.services import OnboardingService
from core.database import engine, get_db
from core.models import detection, publisher, Base
from core.logging_config import setup_logging, logging_middleware, get_logger
from api.access_tokens import router as token_router
from api.detection import router as detection_router
from api.dashboard import router as dashboard_router
from api.onboarding import router as onboarding_router
from api.contact import router as contact_router
from api.auth import router as auth_router
from api.token_metering import router as metering_router
#from api.payments import router as payments_router
import logging

# Initialize logging
setup_logging()
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

# Logging middleware
app.middleware("http")(logging_middleware)

try:
    # Create database tables
    logger.info("Initializing database tables")
    detection.Base.metadata.create_all(bind=engine)
    publisher.Base.metadata.create_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully")
except Exception as e:
    logger.error("Failed to initialize database tables", error=str(e), exc_info=True)
    raise

# Include routers
logger.info("Registering API routers")
routers = [
    (detection_router, "detection"),
    (dashboard_router, "dashboard"),
    (onboarding_router, "onboarding"),
    (auth_router, "auth"),
    (token_router, "access_tokens"),
    (contact_router, "contact"),
    (metering_router, "token_metering")
]

for router, prefix in routers:
    try:
        app.include_router(router)
        logger.debut(f"Registered router: {prefix}")
    except Exception as e:
        logger.error(f"Failed to register router: {prefix}", error=str(e), exc_info=True)
        raise 

# Root endpoint
@app.get("/")
async def root():
    try:
        # Check database connection
        db = next(get_db())
        db_status = "connected"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        db_status = "error"
    
    status_info = {
        "message": "TrainFair Bot Detection System",
        "status": "running",
        "version": "1.0.0",
        "database": db_status
    }
    
    logger.info("Health check completed", **status_info)
    return status_info

# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(
        "HTTP error occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    return {"detail": exc.detail}

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled error occurred",
        error=str(exc),
        path=request.url.path,
        exc_info=True
    )
    return {"detail": "Internal server error"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting TrainFair API server")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_config=None  # Disable uvicorn's default logging
    )