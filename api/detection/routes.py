from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime, timedelta
from core.database import get_db
from pydantic import BaseModel
from .services import BotDetectorService
import logging

router = APIRouter(prefix="/api/v1/detection", tags=["detection"])
logger = logging.getLogger(__name__)

class DetectionRequest(BaseModel):
    publisher_id: str
    
@router.post("")
async def detect_bot(request: Request, detection_request: DetectionRequest, db: Session = Depends(get_db)) -> Dict:
    """
    Endpoint to analyze a request for bot behavior
    Args:
        request: The incoming FastAPI request
        publisher_id: Unique identifier for the publisher
        db: Database session dependency
    
    Returns:
        Dict containing detection results
        
    Raises:
        HTTPException: If there's an error in bot detection
    """
    try:
        detector = BotDetectorService(db)
        results = await detector.analyze_request(request, detection_request.publisher_id)
        return {
            "status": "success",
            "results": results,
        }
    except Exception as e:
        logger.error(f"Error in bot detection: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/stats/{publisher_id}")
async def get_detection_stats(publisher_id: str, time_range: str = "24h", db: Session = Depends(get_db)) -> Dict:
    """ 
    Get detection statistics for a publisher
    
    Args:
        publisher_id: Unique identifier for the publisher
        time_range: Time range for stats (24h, 7d, 30d)
        db: Database session dependency
        
    Returns:
        Dict containing detection statistics
    """
    try:
        detector = BotDetectorService(db)
        stats = await detector.get_detection_stats(publisher_id, time_range)
        return stats
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error getting detection stats: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Error retrieving detection statistics"
        )

@router.get("/ip-reputation/{ip_address}")
async def get_ip_reputation(ip_address: str,db: Session = Depends(get_db)) -> Dict:
    """ 
    Get reputation data for IP address
    
    Args:
        ip_address: IP address to check
        db: Database session dependency
        
    Returns:
        Dict containing IP reputation data    
    """
    try:
        detector = BotDetectorService(db)
        reputation = await detector.get_ip_reputation(ip_address)
        return reputation
        
    except Exception as e:
        logger.error(f"Error getting IP reputation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving IP reputation"
        )

@router.get("/bot-patterns")
async def get_known_patterns(db: Session = Depends(get_db)) -> Dict:
    """ 
    Get list of known bot patterns and their details.
    
    Args:
        db: Database session dependency
        
    Returns:
        Dict containing known bot patterns
    """
    try:
        detector = BotDetectorService(db)
        return {
            "patterns": detector.KNOWN_BOT_PATTERNS
        }
    except Exception as e:
        logger.error(f"Error getting known patterns: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving known bot patterns"
        )

@router.post("/report-false-positive")
async def report_false_positive(request: Request, ip_address: str, db: Session = Depends(get_db)) -> Dict:
    """
    Report a false positive detection.
    
    Args:
        request: The incoming FastAPI request
        ip_address: IP address that was wrongly identified
        db: Database session dependency
        
    Returns:
        Dict containing confirmation of report
    """
    try:
        detector = BotDetectorService(db)
        await detector.handle_false_positive(ip_address)
        return {
            "status": "success",
            "message": "False positive report recorded"
        }
    except Exception as e:
        logger.error(f"Error reporting false positive: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error recording false positive report"
        )

@router.get("/high-risk-ips/{publisher_id}")
async def get_high_risk_ips(publisher_id: str, min_confidence: float = 0.8, db: Session = Depends(get_db)) -> Dict:
    """ 
    Get list of high-risk IPs for a publisher.
    
    Args:
        publisher_id: Unique identifier for the publisher
        min_confidence: Minimum confidence score to include (default: 0.8)
        db: Database session dependency
        
    Returns:
        Dict containing list of high-risk IPs
    """
    try:
        detector = BotDetectorService(db)
        risky_ips = await detector.get_high_risk_ips(publisher_id, min_confidence)
        return {
            "high_risk_ips": risky_ips
        }
    except Exception as e:
        logger.error(f"Error getting high-risk IPs: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving high-risk IPs"
        )