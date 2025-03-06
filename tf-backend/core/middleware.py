# tf-backend/core/middleware.py

from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from .session import SessionManager
from typing import Optional
import logging

logger = logging.getLogger(__name__)
session_manager = SessionManager()

async def get_session(request: Request) -> dict:
    """ 
    Base session verification
    """
    session_id = request.cookies.get("session_id")
    
    logger.debug(f"Cookies in request: {request.cookies}")
    logger.debug(f"Session ID from cookie: {session_id}")
    
    if not session_id:
        logger.warning("No session ID found in cookies")
        raise HTTPException(status_code=401, detail="No session found")
    
    session = session_manager.get_session(session_id)
    
    if not session:
        logger.warning(f"Invalid or expired session ID: {session_id}")
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    logger.debug(f"Valid session found: {session}")

    return session

async def require_publisher(session: dict = Depends(get_session)):
    """Verify the user is a publisher"""
    if session["user_type"] != "publisher":
        logger.warning(f"Access denied - user is not a publisher: {session}")
        raise HTTPException(status_code=403, detail="Publisher access required")
    return session

async def require_ai_company(session: dict = Depends(get_session)):
    """Verify the user is an AI company"""
    if session["user_type"] != "ai-company":
        logger.warning(f"Access denied - user is not an AI company: {session}")
        raise HTTPException(status_code=403, detail="AI Company access required")
    return session

async def verify_session(request: Request):
    """ 
    Verify session middleware
    """
    logger.info(f"Verifying session for path: {request.url.path}")
    logger.info(f"Cookies received: {request.cookies}")
    
    # Skip session check for login/register endpoints
    public_paths = [
        "/api/auth/login", 
        "/api/onboarding/publisher", 
        "/api/onboarding/ai-company",
        "/health"
    ]
    
    if any(request.url.path.startswith(path) for path in public_paths):
        return
    
    session_id = request.cookies.get("session_id")
    
    if not session_id:
        logger.warning("No session_id cookie found")
        raise HTTPException(status_code=401, detail="No session found")
    
    session = session_manager.get_session(session_id)
    logger.info(f"Session found: {session is not None}")
    
    if not session:
        logger.warning("Invalid or expired session")
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    # Add session data to request state
    request.state.session = session
    request.state.user_id = session["user_id"]
    request.state.user_type = session["user_type"]
    logger.info(f"Session verified for user: {session['user_id']}")