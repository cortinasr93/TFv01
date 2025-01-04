from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict
from core.database import get_db
from core.middleware import require_ai_company, require_publisher, get_session
from .services import DashboardService
import logging

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)

# Publisher-specific dashboard
@router.get("/publisher")
async def get_publisher_dashboard(
    session: dict = Depends(require_publisher),
    db: Session = Depends(get_db)
):
    """ 
    Get publisher dashboard data
    """
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_publisher_dashboard(session["user_id"])

# AI Company-specific dashboard
@router.get("/ai-company")
async def get_ai_company_dashboard(
    session: dict = Depends(require_ai_company),
    db: Session = Depends(get_db)
):
    """
    Get AI company dashboard data
    """
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_ai_company_dashboard(session["user_id"])

@router.get("/profile")
async def get_user_profile(
    session: dict = Depends(get_session),
    db: Session = Depends(get_db)
):
    """ 
    Get user profile data
    """
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_user_profile(
        user_id=session["user_id"],
        user_type=session["user_type"]
    )

@router.get("/stats/{publisher_id}")
async def get_publisher_stats(publisher_id: str, db: Session = Depends(get_db)) -> Dict:
    """
    Get basic stats for a publisher.

    Args:
        publisher_id: Unique identifier for the publisher
        db: Database session dependency

    Returns:
        Dict: Dictionary containing basic stats
    """
    try:
        dashboard_service = DashboardService(db)
        stats = await dashboard_service.get_publisher_stats(publisher_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting publisher stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving publisher statistics"
        )

@router.get("/timeseries/{publisher_id}")
async def get_time_series_data(publisher_id: str, db: Session = Depends(get_db)) -> Dict:
    """
    Get time series data for a publisher.
    
    Args:
        publisher_id: Unique identifier for the publisher
        db: Database session dependency
        
    Returns:
        Dictionary containing time series data
    """
    try:
        dashboard_service = DashboardService(db)
        time_series = await dashboard_service.get_time_series_data(publisher_id)
        return time_series
    
    except Exception as e:
        logger.error(f"Error getting time series data: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving time series data"
        )

@router.get("/bot-types/{publisher_id}")
async def get_bot_type_distribution(publisher_id: str, db: Session = Depends(get_db)) -> Dict:
    """
    Get bot type distribution for a publisher.
    
    Args:
        publisher_id: Unique identifier for the publisher
        db: Database session dependency
        
    Returns:
        Dictionary containing bot type distribution data
    """
    try:
        dashboard_service = DashboardService(db)
        bot_types = await dashboard_service.get_bot_type_distribution(publisher_id)
        return bot_types
        
    except Exception as e:
        logger.error(f"Error getting bot type distribution: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving bot type distribution"
        )

@router.get("/recent-detections/{publisher_id}")
async def get_recent_detections(publisher_id: str, db: Session = Depends(get_db)) -> Dict:
    """
    Get recent bot detections for a publisher.
    
    Args:
        publisher_id: Unique identifier for the publisher
        db: Database session dependency
        
    Returns:
        Dictionary containing recent detection data
    """
    try:
        dashboard_service = DashboardService(db)
        detections = await dashboard_service.get_recent_detections(publisher_id)
        return detections
        
    except Exception as e:
        logger.error(f"Error getting recent detections: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving recent detections"
        )

@router.get("/{publisher_id}")
async def get_dashboard_data(
    publisher_id: str, 
    session: dict = Depends(require_publisher), 
    db: Session = Depends(get_db)
) -> Dict:
    """
    Fetch all dashboard data for a publisher

    Args:
        publisher_id (str): Unique identifier for the publisher
        db: database session dependency.

    Returns:
        Dict: Dictionary containing dashboard data inlcuding stats, time series,
              bot types, and recent detections
    
    Raises:
        HTTPException if there's an error retrieving the data.
    """
    try:
        if str(session["user_id"]) != publisher_id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to view this dashboard"
            )
        # Create dashboard service instance
        dashboard_service = DashboardService(db)
        
        # Get dashboard data using service
        dashboard_data = await dashboard_service.get_publisher_dashboard(publisher_id)
        
        return dashboard_data
    
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving dashboard data"
        )