from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.middleware import require_publisher
from .services import OnboardingService
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, Dict
import logging

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])
logger = logging.getLogger(__name__)

class PublisherRegistration(BaseModel):
    name: str
    email: EmailStr
    password: str
    website: HttpUrl
    content_type: str
    settings: Optional[Dict] = None

class AICompanyRegistration(BaseModel):
    company_name: str
    email: EmailStr
    password: str
    website: HttpUrl

@router.post("/publisher")
async def register_publisher(
    registration: PublisherRegistration,
    db: Session = Depends(get_db)
):
    """Register a new publisher and start Stripe onboarding"""
    onboarding_service = OnboardingService(db)
    result = await onboarding_service.register_publisher(
        name=registration.name,
        email=registration.email,
        password=registration.password,
        website=str(registration.website),
        content_type=registration.content_type
    )
    return result

@router.post("/ai-company")
async def register_ai_company(
    registration: AICompanyRegistration,
    db: Session = Depends(get_db)
):
    """Register a new AI company"""
    onboarding_service = OnboardingService(db)
    result = await onboarding_service.register_ai_company(
        company_name=registration.company_name,
        email=registration.email,
        password=registration.password,
        website=str(registration.website)
    )
    return result

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