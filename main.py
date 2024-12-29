from fastapi import FastAPI, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from api.onboarding.services import OnboardingService
from core.database import engine, get_db
from core.models import detection, publisher, Base
from api.detection import router as detection_router
from api.dashboard import router as dashboard_router
#from api.payments import router as payments_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="TrainFair Bot Detection System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Create database tables
detection.Base.metadata.create_all(bind=engine)
publisher.Base.metadata.create_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(detection_router)
app.include_router(dashboard_router)
#app.include_router(payments_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "TrainFair Bot Detection System",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/dashboard")
async def get_dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard/index.html",
        {"request": request}
    )

@app.get("/register")
async def get_registration_page(request: Request):
    return templates.TemplateResponse(
        "registration/index.html",
        {"request": request}
    )

@app.get("/register/publisher")
async def get_publisher_registration(request: Request):
    return templates.TemplateResponse(
        "registration/publisher.html",
        {"request": request}
    )

@app.post("/api/v1/onboarding/publisher")
async def register_publisher(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        data = await request.json()
        onboarding_service = OnboardingService(db)
        result = await onboarding_service.register_publisher(
            name=data.get("name"),
            email=data.get("email"),
            password=data.get("password"),
            website=data.get("website"),
            content_type=data.get("contentType")
        )
        return result
    except Exception as e:
        logger.error(f"Error in publisher registration: {e}")
        raise HTTPException(
            status_code=500,
            detail="Registration failed"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)