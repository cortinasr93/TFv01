from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine
from core.models import detection, publisher
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)