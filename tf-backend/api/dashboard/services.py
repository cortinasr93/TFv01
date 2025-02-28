# tf-backend/api/dashboard/services.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from typing import Dict, List
import json
from core.models.detection import RequestLog
from core.models.publisher import Publisher
from core.models.aicompany import AICompany
from core.logging_config import get_logger, LogOperation
from core.models.payment import UsageRecord, UsageStatus, PaymentTransaction, PublisherStripeAccount, AICompanyPaymentAccount

logger = get_logger(__name__)

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        
    async def get_publisher_dashboard(self, publisher_id: str) -> Dict:
        """
        Get all dashboard data for a publisher
        """
        with LogOperation("get_publisher_dashboard", publisher_id=publisher_id):
            try:
                
                publisher = self.db.query(Publisher).filter(Publisher.id == publisher_id).first()
                if not publisher:
                    logger.error("publisher_not_found", publisher_id=publisher_id)
                    raise HTTPException(status_code=404, detail="Publisher not found")
                
                now = datetime.now(timezone.utc)
                last_24h = now - timedelta(hours=24)
                last_hour = now - timedelta(hours=1)
                
                logger.info("fetching_publisher_dashboard",
                        publisher_id=publisher_id,
                        publisher_name=publisher.name)
            
                # Get all components of the dashboard
                stats = await self.get_publisher_stats(publisher_id, last_24h)
                time_series = await self.get_publisher_time_series_data(publisher_id, last_24h)
                bot_types = await self.get_bot_type_distribution(publisher_id, last_24h)
                recent_detections = await self.get_recent_detections(publisher_id)
                earnings = await self.get_publisher_earnings(publisher_id)
            
                logger.info("dashboard_data_collected",
                          publisher_id=publisher_id,
                          stats_collected=bool(stats),
                          time_series_points=len(time_series),
                          bot_types_found=len(bot_types),
                          detections_count=len(recent_detections))
                
                return {
                    "publisherName": publisher.name,
                    "stats": stats,
                    "timeSeriesData": time_series,
                    "botTypes": bot_types,
                    "recentDetections": recent_detections,
                    "earnings": earnings
                }
                
            except Exception as e:
                logger.error("dashboard_fetch_failed",
                           publisher_id=publisher_id,
                           error=str(e),
                           exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail="Error retrieving dashboard data"
                )
    
    async def get_ai_company_dashboard(self, company_id: str) -> Dict:
        """ 
        Get AI company-specific dashboard data
        """
        with LogOperation("get_ai_company_dashboard", company_id=company_id):
            try:
                now = datetime.now(timezone.utc)
                last_30d = now - timedelta(days=30)
                
                # Get company information
                company = self.db.query(AICompany).filter(AICompany.id == company_id).first()
                if not company:
                    logger.error("company_not_found", company_id=company_id)
                    raise HTTPException(status_code=404, detail="AI Company not found")
                
                logger.info("fetching_company_dashboard",
                          company_id=company_id,
                          company_name=company.name)
                
                usage_stats = await self.get_api_usage_stats(company_id)
                time_series = await self.get_usage_time_series(company_id, last_30d)
                data_sources = await self.get_data_sources(company_id)
                recent_transactions = await self.get_recent_transactions(company_id)

                logger.info("company_dashboard_collected",
                          company_id=company_id,
                          stats_collected=bool(usage_stats),
                          time_series_points=len(time_series),
                          data_sources_count=len(data_sources),
                          transactions_count=len(recent_transactions))
                
                return {
                    "companyName": company.name,
                    "usage_stats": usage_stats,
                    "timeSeriesData": time_series,
                    "recentTransactions": recent_transactions,
                    "dataSources": data_sources
                }
            except Exception as e:
                logger.error("company_dashboard_fetch_failed",
                           company_id=company_id,
                           error=str(e),
                           exc_info=True)
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
    
    async def get_publisher_stats(self, publisher_id: str, since: datetime) -> Dict:
        """
        Get basic statistics for a publisher
        """
        with LogOperation("get_publisher_stats", publisher_id=publisher_id):
            try:
                now = datetime.now(timezone.utc)
                last_24h = now - timedelta(hours=24)
                last_hour = now - timedelta(hours=1)
                
                # Calculate basic stats
                total_requests = self.db.query(RequestLog).filter(
                    RequestLog.publisher_id == publisher_id,
                    RequestLog.timestamp >= since
                ).count()
                
                bot_requests = self.db.query(RequestLog).filter(
                    RequestLog.publisher_id == publisher_id,
                    RequestLog.timestamp >= since,
                    RequestLog.is_bot == True
                ).count()
                
                unique_ips = self.db.query(func.count(func.distinct(RequestLog.ip_address))).filter(
                    RequestLog.publisher_id == publisher_id,
                    RequestLog.timestamp >= since,
                ).scalar()
                
                active_threats = self.db.query(RequestLog).filter(
                    RequestLog.publisher_id == publisher_id,
                    RequestLog.timestamp >= since,
                    RequestLog.is_bot == True,
                    RequestLog.confidence_score >= 0.8
                ).count()
                
                stats = {
                    "totalRequests": total_requests,
                    "botPercentage": round(bot_requests / total_requests * 100 if total_requests > 0 else 0, 1),
                    "activeThreats": active_threats,
                    "uniqueIPs": unique_ips
                }
                
                logger.info("publisher_stats_calculated",
                           publisher_id=publisher_id,
                           total_requests=total_requests,
                           bot_requests=bot_requests,
                           unique_ips=unique_ips,
                           active_threats=active_threats)
                
                return stats
            
            except Exception as e:
                logger.error("stats_calculation_failed",
                           publisher_id=publisher_id,
                           error=str(e),
                           exc_info=True)
                raise
    
    async def get_publisher_time_series_data(self, publisher_id: str, since: datetime) -> List[Dict]:
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
    
    async def get_publisher_earnings(self, publisher_id: str) -> Dict:
        """ 
        Get earnings data for a publisher (manual processing for MVP)
        """
        with LogOperation("get_publisher_earnings", publisher_id=publisher_id):
            try:
                # publisher_account = self.db.query(PublisherStripeAccount).filter(
                #     PublisherStripeAccount.publisher_id == publisher_id
                # ).first()
                               
                # if not publisher_account:
                #     logger.warning("no_stripe_account_found", publisher_id=publisher_id)
                #     return {
                #         "currentBalance": 0,
                #         "lastPayout": None,
                #         "totalEarned": 0
                #     }
                
                # total_earned = self.db.query(func.sum(UsageRecord.publisher_amount)).filter(
                #     UsageRecord.publisher_id == publisher_account.id,
                #     UsageRecord.status == UsageStatus.PROCESSED
                # ).scalar() or 0
                
                usage_records = self.db.query(UsageRecord).filter(
                    UsageRecord.publisher_id == publisher_id
                ).all()
                
                total_earned = sum(record.publisher_amount for record in usage_records) or 0
                
                logger.info("earnings_calculated",
                           publisher_id=publisher_id,
                           total_earned=total_earned,
                           #current_balance=publisher_account.current_balance,
                           #last_payout=publisher_account.last_payout_at
                           )
                
                return {
                    "currentBalance": total_earned,
                    "lastPayout": None, #No payouts yet through the system
                    "totalEarned": total_earned
                }
            
            except Exception as e:
                logger.error("earnings_calculation_failed",
                           publisher_id=publisher_id,
                           error=str(e),
                           exc_info=True)
                raise
    
    async def get_bot_type_distribution(self, publisher_id: str, since: datetime) -> List[Dict]:
        """ 
        Get bot type distribution for a publisher
        """
      
        bot_types = self.db.query(
            RequestLog.bot_name,
            func.count(RequestLog.id).label('count')
        ).filter(
            RequestLog.publisher_id == publisher_id,
            RequestLog.timestamp >= since,
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
    
    async def get_usage_stats(self, company_id: str) -> Dict:
        """ 
        Get usage statistics for AI company
        """
        payment_account = self.db.query(AICompanyPaymentAccount).filter(
            AICompanyPaymentAccount.company_id == company_id
        ).first()
        
        if not payment_account:
            return {
                "totalTokens": 0,
                "totalCost": 0,
                "publishersAccessed": 0,
                "averageCostPerToken": 0
            }
        
        total_tokens = self.db.query(func.sum(UsageRecord.amount)).filter(
            UsageRecord.company_id == payment_account.id
        ).scalar() or 0
        
        total_cost = self.db.query(func.sum(UsageRecord)).filter(
            UsageRecord.company_id == payment_account.id,
            UsageRecord.status == UsageStatus.PROCESSED
        ).scalar() or 0
        
        unique_publishers = self.db.query(func.count(func.distinct(UsageRecord.publisher_id))).filter(
            UsageRecord.company_id == payment_account.id
        ).scalar() or 0
        
        return {
            "totalTokens": total_tokens,
            "totalCost": total_cost,
            "publishersAccessed": unique_publishers,
            "averageCostPerToken": total_cost / total_tokens if total_tokens > 0 else 0
        }
    
    async def get_usage_time_series(self, company_id: str, since: datetime) -> List[Dict]:
        """Get usage time series data for AI company"""
        time_series = []
        now = datetime.now(timezone.utc)
        
        for i in range(30):
            day_start = now - timedelta(days=i+1)
            day_end = now - timedelta(days=i)
            
            records = self.db.query(UsageRecord).filter(
                UsageRecord.company_id == company_id,
                UsageRecord.created_at.between(day_start, day_end)
            ).all()
            
            tokens = sum(r.amount for r in records)
            cost = sum(r.amount for r in records if r.status == UsageStatus.PROCESSED)
            
            time_series.append({
                "time": day_start.strftime("%Y-%m-%d"),
                "tokens": tokens,
                "cost": cost
            })
        
        return time_series[::-1]
    
    async def get_data_sources(self, company_id: str) -> List[Dict]:
        """ 
        Get data source information for AI company
        """
        try:
            payment_account = self.db.query(AICompanyPaymentAccount).filter(
                AICompanyPaymentAccount.company_id == company_id
            ).first()
            
            if not payment_account:
                return []
            
            usage_by_publisher = self.db.query(
                UsageRecord.publisher_id,
                func.sum(UsageRecord.num_tokens).label('total_tokens'),
                func.sum(UsageRecord.total_cost).label('total_cost'),
                func.sum(UsageRecord.publisher_amount).label('publisher_earned'),
                func.max(UsageRecord.created_at).label('last_accessed')
            ).filter(
                UsageRecord.company_id == company_id,
                UsageRecord.status == UsageStatus.PROCESSED 
            ).group_by(UsageRecord.publisher_id).all()
        
            data_sources = []
            for record in usage_by_publisher:
                publisher_account = self.db.query(PublisherStripeAccount).filter_by(id=record.publisher_id).first()
                
                if publisher_account:
                    publisher = self.db.query(Publisher).filter_by(
                        id=publisher_account.publisher_id
                    ).first()
                    if publisher:
                        data_sources.append({
                            "publisherId": str(publisher.id),
                            "publisherName": publisher.name,
                            "tokensUsed": record.total_tokens,
                            "cost": record.total_cost,
                            "publisherEarned": record.publisher_earned,
                            "lastAccessed": record.last_accessed.isoformat(),
                            "contentType": publisher.content_type
                        })
        
            return sorted(data_sources, key=lambda x: x['tokensUsed'], reverse=True)
        except Exception as e:
                logger.error(f"Error getting data sources: {str(e)}")
                raise
    
    async def get_recent_transactions(self, company_id: str) -> List[Dict]:
        """Get recent payment transactions for AI company"""
        
        try:
            payment_account = self.db.query(AICompanyPaymentAccount).filter(
                AICompanyPaymentAccount.company_id == company_id
            ).first()
            
            if not payment_account:
                return []
            
            transactions = self.db.query(PaymentTransaction).filter(
                PaymentTransaction.company_id == payment_account.id
            ).order_by(PaymentTransaction.created_at.desc()).limit(10).all()
            
            return [{
                "id": str(tx.id),
                "date": tx.created_at.isoformat(),
                "amount": tx.amount,
                "description": f"Payment for usage - {tx.stripe_payment_intent_id}",
                "status": tx.status
            } for tx in transactions]
        except Exception as e:
            logger.error(f"Error getting recent transactions: {str(e)}")
            raise
    
    async def get_api_usage_stats(self, company_id: str) -> Dict:
        """ 
        Get usage stats for AI company
        """
        with LogOperation("get_api_usage_stats", company_id=company_id):
            try:
                payment_account = self.db.query(AICompanyPaymentAccount).filter(
                    AICompanyPaymentAccount.company_id == company_id
                ).first()
                
                if not payment_account:
                    logger.warning("no_payment_account_found", company_id=company_id)
                    return{
                        "totalTokens": 0,
                        "totalCost": 0,
                        "publishersAccessed": 0,
                        "averageCostPerToken": 0
                    }
                total_tokens = self.db.query(func.sum(UsageRecord.num_tokens)).filter(
                    UsageRecord.company_id == payment_account.id
                ).scalar() or 0
                
                total_cost = self.db.query(func.sum(UsageRecord.total_cost)).filter(
                    UsageRecord.company_id == payment_account.id,
                    UsageRecord.status == UsageStatus.PROCESSED
                ).scalar() or 0
                
                unique_publishers = self.db.query(
                    func.count(func.distinct(UsageRecord.publisher_id))
                ).filter(
                    UsageRecord.company_id == payment_account.id
                ).scalar() or 0
                
                stats = {
                    "totalTokens": total_tokens,
                    "totalCost": total_cost,
                    "publishersAccessed": unique_publishers,
                    "averageCostPerToken": total_cost / total_tokens if total_tokens > 0 else 0
                }
                
                logger.info("usage_stats_calculated",
                           company_id=company_id,
                           total_tokens=total_tokens,
                           total_cost=total_cost,
                           publishers_accessed=unique_publishers)
                
                return stats
            
            except Exception as e:
                logger.error("usage_stats_calculation_failed",
                           company_id=company_id,
                           error=str(e),
                           exc_info=True)
                raise
    
    async def get_usage_time_series(self, company_id: str, since: datetime) -> List[Dict]:
        """Get usage time series data for AI company"""
        try:
            payment_account = self.db.query(AICompanyPaymentAccount).filter(
                AICompanyPaymentAccount.company_id == company_id
            ).first()
            
            if not payment_account:
                return []
            
            time_series = []
            now = datetime.now(timezone.utc)
            
            for i in range(30):
                day_start = now - timedelta(days=i+1)
                day_end = now - timedelta(days=i)
                
                records = self.db.query(UsageRecord).filter(
                    UsageRecord.company_id == payment_account.id,
                    UsageRecord.created_at.between(day_start, day_end)
                ).all()
                
                tokens = sum(r.num_tokens for r in records)
                cost = sum(r.total_cost for r in records if r.status == UsageStatus.PROCESSED)
                
                time_series.append({
                    "time": day_start.strftime("%Y-%m-%d"),
                    "tokens": tokens,
                    "cost": cost
                })
            
            return time_series[::-1]  # Return in chronological order
        except Exception as e:
            logger.error(f"Error getting usage time series: {str(e)}")
            raise
        
    
            