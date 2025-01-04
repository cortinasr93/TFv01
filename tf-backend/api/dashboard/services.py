from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from typing import Dict, List
import logging
import json
from core.models.detection import RequestLog
from core.models.publisher import Publisher
from core.models.aicompany import AICompany

logger = logging.getLogger(__name__)

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        
    async def get_publisher_dashboard(self, publisher_id: str) -> Dict:
        """
        Get all dashboard data for a publisher
        """
        try:
            now = datetime.now(timezone.utc)
            last_24h = now - timedelta(hours=24)
            last_hour = now - timedelta(hours=1)
        
            # Get all components of the dashboard
            stats = await self.get_publisher_stats(publisher_id)
            time_series = await self.get_time_series_data(publisher_id)
            bot_types = await self.get_bot_type_distribution(publisher_id)
            recent_detections = await self.get_recent_detections(publisher_id)
        
            return {
                "stats": stats,
                "timeSeriesData": time_series,
                "botTypes": bot_types,
                "recentDetections": recent_detections
            }
            
        except Exception as e:
            logger.error(f"Error getting publisher dashboard: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error retrieving dashboard data"
            )
    
    async def get_ai_company_dashboard(self, company_id: str) -> Dict:
        """ 
        Get AI company-specific dashboard data
        """
        try:
            return {
                "usage_stats": await self.get_api_usage_stats(company_id),
                "billing": await self.get_billing_summary(company_id),
                "recent_transactions": await self.get_recent_transactions(company_id),
                "data_sources": await self.get_data_source_stats(company_id)
            }
        except Exception as e:
            logger.error(f"Error getting AI company dashboard: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error retrieving dashboard data"
            )
    async def get_user_profile(self, user_id: str, user_type: str) -> Dict:
        """ 
        Get user profile data
        """
        try:
            if user_type == "publisher":
                user = self.db.query(Publisher).filter_by(id=user_id).first()
            else:
                user = self.db.query(AICompany).filter_by(id=user_id).first()
                
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return {
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at,
                "settings": user.settings if hasattr(user, 'settings') else {}
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error retrieving user profile"
            )
    
    async def get_publisher_stats(self, publisher_id: str) -> Dict:
        """
        Get basic statistics for a publisher
        """
        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)
        last_hour = now - timedelta(hours=1)
        
        # Calculate basic stats
        total_requests = self.db.query(RequestLog).filter(
            RequestLog.publisher_id == publisher_id,
            RequestLog.timestamp >= last_24h
        ).count()
        
        bot_requests = self.db.query(RequestLog).filter(
            RequestLog.publisher_id == publisher_id,
            RequestLog.timestamp >= last_24h,
            RequestLog.is_bot == True
        ).count()
        
        unique_ips = self.db.query(func.count(func.distinct(RequestLog.ip_address))).filter(
            RequestLog.publisher_id == publisher_id,
            RequestLog.timestamp >= last_24h
        ).scalar()
        
        active_threats = self.db.query(RequestLog).filter(
            RequestLog.publisher_id == publisher_id,
            RequestLog.timestamp >= last_hour,
            RequestLog.is_bot == True,
            RequestLog.confidence_score >= 0.8
        ).count()
        
        return {
            "totalRequests": total_requests,
            "botPercentage": round(bot_requests / total_requests * 100 if total_requests > 0 else 0, 1),
            "activeThreats": active_threats,
            "uniqueIPs": unique_ips
        }
    
    async def get_time_series_data(self, publisher_id: str) -> List[Dict]:
        """ 
        Get time series data for a publisher
        """
        now = datetime.now(timezone.utc)
        time_series = []
        
        for i in range(24):
            hour_start = now - timedelta(hours=i+1)
            hour_end = now - timedelta(hours=i)
            
            total = self.db.query(RequestLog).filter(
                RequestLog.publisher_id == publisher_id,
                RequestLog.timestamp.between(hour_start, hour_end)
            ).count()
            
            bots = self.db.query(RequestLog).filter(
                RequestLog.publisher_id == publisher_id,
                RequestLog.timestamp.between(hour_start, hour_end),
                RequestLog.is_bot == True
            ).count()
            
            time_series.append({
                "time": hour_start.strftime("%H:00"),
                "total": total,
                "bots": bots,
            })
        
        return time_series[::-1]
    
    async def get_bot_type_distribution(self, publisher_id: str) -> List[Dict]:
        """ 
        Get bot type distribution for a publisher
        """
        
        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)
        
        bot_types = self.db.query(
            RequestLog.bot_name,
            func.count(RequestLog.id).label('count')
        ).filter(
            RequestLog.publisher_id == publisher_id,
            RequestLog.timestamp >= last_24h,
            RequestLog.is_bot == True,
            RequestLog.bot_name != None,
        ).group_by(RequestLog.bot_name).all()
        
        return [
            {"name": bt[0], "value": bt[1]}
            for bt in bot_types
        ]
    
    async def get_recent_detections(self, publisher_id: str) -> List[Dict]:
        """ 
        Get recent bot detections for a publisher
        """
        recent_detections = self.db.query(RequestLog).filter(
            RequestLog.publisher_id == publisher_id,
            RequestLog.is_bot == True
        ).order_by(
            RequestLog.timestamp.desc()
        ).limit(10).all()
        
        detection_data = []
        for detection in recent_detections:
            detection_methods = json.loads(detection.detection_methods)
            detection_data.append({
                "time": detection.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "ipAddress": detection.ip_address,
                "botType": detection.bot_name or "Unkown",
                "confidence": round(detection.confidence_score * 100, 1),
                'detectionMethod': ", ".join(detection_methods)
            })
        
        return detection_data