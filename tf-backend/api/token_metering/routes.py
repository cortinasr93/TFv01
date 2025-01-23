# tf-backend/api/token_metering/routes.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel
from core.database import get_db
from core.middleware import require_publisher, require_ai_company
from .services import TokenMeteringService
import logging

router = APIRouter(prefix="/api/token_metering", tags=["token-metering"])
logger = logging.getLogger(__name__)

class ContentAnalysisRequest(BaseModel):
    content: str
    token: str
    publisher_id: str

class UsageAnalyticsRequest(BaseModel):
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    
class ContentAnalysisResponse(BaseModel):
    token_count: int
    content_size_bytes: int
    content_type: str
    estimated_cost: float
    allowed: bool
    usage_id: Optional[str]

@router.post("/analyze-content", response_model=ContentAnalysisResponse)
async def analyze_content(
    request: ContentAnalysisRequest,
    db: Session = Depends(get_db)
):
    """Analyze content and track token usage"""
    try:
        metering_service = TokenMeteringService(db)
        result = await metering_service.process_bot_request(
            token=request.token,
            publisher_id=request.publisher_id,
            content=request.content
        )
        
        if not result['allowed']:
            raise HTTPException(
                status_code=403,
                detail=result.get('reason', 'Access denied')
            )
        
        return {
            'token_count': result['tokens_processed'],
            'content_size_bytes': result['content_analysis']['content_size_bytes'],
            'content_type': result['content_analysis']['content_type'],
            'estimated_cost': result['cost'],
            'allowed': True,
            'usage_id': result['usage_id']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error processing content analysis"
        )

@router.get("/publisher/{publisher_id}/usage")
async def get_publisher_usage(
    publisher_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: dict = Depends(require_publisher),
    db: Session = Depends(get_db)
):
    """
    Get token usage statistics for a publisher
    """
    # Verify publisher is requesting their own usage
    if str(session["user_id"]) != publisher_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this publisher's usage"
        )

    try:
        metering_service = TokenMeteringService(db)
        usage_stats = await metering_service.get_usage_analytics(
            publisher_id=publisher_id,
            start_date=start_date,
            end_date=end_date
        )
        return usage_stats

    except Exception as e:
        logger.error(f"Error getting publisher usage: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving usage statistics"
        )

@router.get("/ai-company/{company_id}/usage")
async def get_company_usage(
    company_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: dict = Depends(require_ai_company),
    db: Session = Depends(get_db)
):
    """
    Get token usage statistics for an AI company
    """
    # Verify company is requesting their own usage
    if str(session["user_id"]) != company_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this company's usage"
        )

    try:
        metering_service = TokenMeteringService(db)
        usage_stats = await metering_service.get_usage_analytics(
            company_id=company_id,
            start_date=start_date,
            end_date=end_date
        )
        return usage_stats

    except Exception as e:
        logger.error(f"Error getting company usage: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving usage statistics"
        )

@router.post("/validate-bot-request")
async def validate_bot_request(
    request: Request,
    publisher_id: str,
    token: str,
    db: Session = Depends(get_db)
): 
    """Validate bot request and track usage"""
    try:
        # Get request body content
        content = await request.body()
        content_str = content.decode()
        
        # Collect request metadata
        metadata = {
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "path": str(request.url.path),
            "method": request.method,
            "headers": dict(request.headers)
        }
        
        metering_service = TokenMeteringService(db)
        result = await metering_service.process_bot_request(
            token=token,
            publisher_id=publisher_id,
            content=content_str,
            request_metadata=metadata
        )
        
        return {
            "allowed": result['allowed'],
            "message": "Access granted" if result['allowed'] else result.get('reason', 'Access denied'),
            "usage_data": {
                "tokens_processed": result.get('tokens_processed'),
                "cost": result.get('cost'),
                "content_type": result.get('content_analysis', {}).get('content_type')
            } if result['allowed'] else None
        }
    
    except Exception as e:
        logger.error(f"Error validating bot request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error validating request"
        )