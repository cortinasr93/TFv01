# tf-backend/main.py

from fastapi import FastAPI, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from api.onboarding.services import OnboardingService
from core.database import engine, get_db
from core.models import detection, publisher, Base
from core.logging_config import setup_logging, logging_middleware, get_logger
from core.config import get_settings
from api.access_tokens import router as token_router
from api.detection import router as detection_router
from api.dashboard import router as dashboard_router
from api.onboarding import router as onboarding_router
from api.contact import router as contact_router
from api.auth import router as auth_router
from api.token_metering import router as metering_router
#from api.payments import router as payments_router

# Initialize settings
settings = get_settings()

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TrainFair Bot Detection System",
    #root_path="/api",
    #root_path_in_servers=False
)

@app.middleware("http")
async def cors_debug_middleware(request: Request, call_next):
    logger.debug(f"Request origin: {request.headers.get('origin')}")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    
    response = await call_next(request)
    
    logger.debug(f"CORS response headers: {dict(response.headers)}")
    return response

class PreflightMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            try:
                response = Response()
                # Get origin from request headers
                origin = request.headers.get("origin", "")
                allowed_origins = [
                    settings.FRONTEND_URL,
                    f"https://www.{settings.FRONTEND_URL.replace('https://', '')}",
                    "http://localhost:3000",
                    "http://127.0.0.1:3000"
                ] if settings.FRONTEND_URL else [
                    "http://localhost:3000",
                    "http://127.0.0.1:3000"
                ]
                # Check if origin is allowed
                if origin in allowed_origins:
                    logger.debug(f"Origin {origin} is allowed")
                    response.headers["Access-Control-Allow-Origin"] = origin
                    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
                    response.headers["Access-Control-Allow-Headers"] = (
                        "Content-Type, Authorization, Accept, Origin, "
                        "X-Requested-With, X-CSRF-Token, Cookie"
                    )
                    response.headers["Access-Control-Allow-Credentials"] = "true"
                    response.headers["Access-Control-Max-Age"] = "3600"
                else:
                    logger.warning(f"Origin {origin} not in allowed origins: {allowed_origins}")
                return response
            except Exception as e:
                logger.error(f"Error in preflight handling: {str(e)}", exc_info=True)
                raise
        return await call_next(request)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,  # From your existing settings
        f"https://www.{settings.FRONTEND_URL.replace('https://', '')}",  # www subdomain
        "http://localhost:3000",  # Local development
        "http://127.0.0.1:3000",  # Alternative local development
    ] if settings.FRONTEND_URL else [
        "http://localhost:3000",  # Fallback for development
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-CSRF-Token",
        "Cookie"
    ],
    expose_headers=[
        "Set-Cookie",
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Credentials"
    ],
    max_age=3600,
)

# Custom middlewares
app.middleware("http")(cors_debug_middleware)
app.add_middleware(PreflightMiddleware)
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
        logger.debug(f"Registered router: {prefix}")
    except Exception as e:
        logger.error(f"Failed to register router: {prefix}", error=str(e), exc_info=True)
        raise 

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "TrainFair Bot Detection System",
        "status": "running",
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
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

# Temporary checking routes
@app.get("/routes")
def get_routes():
    routes = []
    for route in app.routes:
        routes.append(f"{route.methods} {route.path}")
    return {"routes": routes}

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