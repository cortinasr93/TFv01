# tf-backend/api/onboarding/routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.middleware import require_publisher
from .services import OnboardingService
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, Dict, List
from fastapi.responses import JSONResponse
import logging

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])
logger = logging.getLogger(__name__)

class PublisherRegistration(BaseModel):
    name: str
    email: EmailStr
    company_name: str
    # password: str
    website: HttpUrl
    content_type: str
    message: Optional[str] = None
    settings: Optional[Dict] = None

class AICompanyRegistration(BaseModel):
    name: str
    company_name: str
    email: EmailStr
    # password: str
    website: HttpUrl
    use_cases: List[str]
    message: Optional[str] = None

@router.post("/publisher")
async def register_publisher(
    registration: PublisherRegistration,
    db: Session = Depends(get_db)
):
    """Register a new publisher and start Stripe onboarding"""
    try:
        onboarding_service = OnboardingService(db)
        result = await onboarding_service.register_publisher(
            name=registration.name,
            email=registration.email,
            company_name=registration.company_name,
            # password=registration.password,
            website=str(registration.website),
            content_type=registration.content_type,
            message=registration.message
        )
        
        logger.info(f"Successfully registered publisher: {registration.company_name}")
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Publisher registration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/ai-company")
async def register_ai_company(
    registration: AICompanyRegistration,
    db: Session = Depends(get_db)
):
    """Register a new AI company"""
    try:
        onboarding_service = OnboardingService(db)
        result = await onboarding_service.register_ai_company(
            name=registration.name,
            company_name=registration.company_name,
            email=registration.email,
            # password=registration.password,
            website=str(registration.website),
            use_cases=registration.use_cases,
            message=registration.message
        )
        logger.info(f"Successfully registered AI company: {registration.company_name}")
        return result
    except Exception as e:
        logger.error(f"AI company registration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/publisher/{publisher_id}/complete")
async def complete_publisher_onboarding(
    publisher_id: str,
    db: Session = Depends(get_db)
):
    """Complete the publisher onboarding process"""
    
    try: 

        logger.info(f"Completing onboarding for publisher: {publisher_id}")
        onboarding_service = OnboardingService(db)
        result = await onboarding_service.complete_publisher_onboarding(publisher_id)
        logger.info(f"Onboarding completion result: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Error completing publisher onboarding: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error completing onboarding: {str(e)}"
        )

@router.post("/publisher/{publisher_id}/refresh-link")
async def refresh_onboarding_link(
    publisher_id: str,
    session: dict = Depends(require_publisher),
    db: Session = Depends(get_db)
):
    """Refresh the Stripe onboarding link if it expired"""
    # Verify user is refreshing their own link
    if str(session["user_id"]) != publisher_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to refresh this onboarding link"
        )
    
    try:
        onboarding_service = OnboardingService(db)
        new_url = await onboarding_service.refresh_account_link(publisher_id)
        return {"onboardingUrl": new_url}
        
    except Exception as e:
        logger.error(f"Error refreshing onboarding link: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to refresh onboarding link"
        )