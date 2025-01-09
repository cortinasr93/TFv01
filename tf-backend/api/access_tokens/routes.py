from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, UUID4
from core.database import get_db
from core.middleware import require_ai_company, require_publisher
from core.models.access_tokens import AccessType, AccessTokenStatus
from .services import AccessTokenService
import logging

router = APIRouter(prefix="api/access-tokens", tags=["access-tokens"])
logger = logging.getLogger(__name__)

class TokenCreationResponse(BaseModel):
    token: str
    company_id: UUID4
    created_at: datetime

class ValidationResponse(BaseModel):
    valid: bool
    message: Optional[str] = None

class UsageRecord(BaseModel):
    timestamp: datetime
    request_path: str
    ai_tokens_processed: int
    content_type: Optional[str]
    content_size_bytes: Optional[int]
    is_success: bool
    error_message: Optional[str]

@router.post("/company/{company_id}", response_model=TokenCreationResponse)
async def create_company_token(
    company_id: str,
    session: dict = Depends(require_ai_company),
    db: Session = Depends(get_db)
):
    """Create a new access token for an AI company after setup payment"""
    # Verify company is requesting their own token
    if session["user_id"] != company_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create token for this company"
        )
    
    try:
        token_service = AccessTokenService(db)
        token = await token_service.create_company_token(company_id)
        
        return {
            "token": token.token,
            "company_id": token.company_id,
            "created_at": token.created_at
        }
    
    except Exception as e:
        logger.error(f"Error creating company token: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Error creating access token"
        )

@router.post("/validate", response_model=ValidationResponse)
async def validate_token(
    request: Request,
    publisher_id: str,
    token: str,
    db: Session = Depends(get_db)
):
    """Validate an access token for a specific publisher"""
    try:
        # Collect request metadata
        metadata = {
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "path": str(request.url.path),
            "headers": dict(request.headers)
        }

        token_service = AccessTokenService(db)
        is_valid = await token_service.validate_token_for_publisher(
            publisher_id=publisher_id,
            token=token,
            request_metadata=metadata
        )
        
        return {
            "valid": is_valid,
            "message": "Token validated successfully" if is_valid else "Invalid token or access denied"
        }
        
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error validating token"
        )

@router.post("/publisher/{publisher_id}/block-company")
async def block_company_access(
    publisher_id: str,
    company_id: str,
    reason: Optional[str] = None,
    session: dict = Depends(require_publisher),
    db: Session = Depends(get_db)
):
    """Block an AI company's access to publisher content"""
    if session["user_id"] != publisher_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to modify this publisher's access controls"
        )
    
    try:
        token_service = AccessTokenService(db)
        success = await token_service.remove_token_from_publisher(
            publisher_id=publisher_id,
            company_id=company_id,
            block_reason=reason
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to block company access"
            )
        
        return {
            "status": "success", 
            "message": "Company access blocked successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error blocking company access: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error modifying access controls"
        )

@router.get("/usage/{token_id}", response_model=List[UsageRecord])
async def get_token_usage(
    token_id: str,
    publisher_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: dict = Depends(require_ai_company),
    db: Session = Depends(get_db)
):
    """Get usage history for a token"""
    try:
        token_service = AccessTokenService(db)
        usage_records = await token_service.get_token_usage(
            token_id=token_id,
            publisher_id=publisher_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return [
            {
                "timestamp": record.timestamp,
                "request_path": record.request_path,
                "ai_tokens_processed": record.ai_tokens_processed,
                "content_type": record.content_type,
                "content_size_bytes": record.content_size_bytes,
                "is_success": record.is_success,
                "error_message": record.error_message
            }
            for record in usage_records
        ]
    
    except Exception as e:
        logger.error(f"Error getting token usage: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving usage data"
        )

@router.post("/{token_id}/revoke")
async def revoke_token(
    token_id: str,
    session: dict = Depends(require_ai_company),
    db: Session = Depends(get_db)
):
    """Revoke an access token"""
    try:
        token_service = AccessTokenService(db)
        success = await token_service.revoke_token(token_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Token not found"
            )
        
        return {
            "status": "success",
            "message": "Token revoked successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking token: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error revoking token"
        )