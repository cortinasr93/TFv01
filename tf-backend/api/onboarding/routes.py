from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from .services import OnboardingService
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, Dict

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

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
    onboarding_service = OnboardingService(db)
    result = await onboarding_service.complete_publisher_onboarding(publisher_id)
    return result