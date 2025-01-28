# tf-backend/api/access_tokens/services.py

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from typing import Optional, Dict, List
import jwt
import json
import redis
import secrets
from redis.exceptions import RedisError
from core.redis_client import RedisClientFactory
from core.models.access_tokens import AccessToken, AccessTokenStatus, APIUsageRecord
from core.config import get_settings
from core.logging_config import get_logger, LogOperation

logger = get_logger(__name__)
settings = get_settings()

class AccessTokenService:
    def __init__(self, db: Session):
        self.db = db
        self.secret_key = settings.JWT_SECRET_KEY
        
        try: 
            # Initialize Redis connection
            self.redis = RedisClientFactory.get_client()
        except RedisError as e:
            logger.error(f"Failed to initialize Redis connection: {str(e)}")
            raise
        
    async def create_company_token(self, company_id: str) -> AccessToken:
        """ 
        Create new access token for AI company
        """
        with LogOperation("create_company_token", company_id=company_id):
            try:
                # Check if company already has a token
                existing_token = self.db.query(AccessToken).filter(
                    AccessToken.company_id == company_id,
                    AccessToken.status == AccessTokenStatus.ACTIVE
                ).first()
                
                if existing_token:
                    logger.info(f"Company {company_id} already has an active token")
                    return existing_token
                
                # Generate secure token using JWT
                token_payload = {
                    "company_id": str(company_id),
                    "jti": secrets.token_hex(16), # Unique token ID
                    "iat": datetime.now(timezone.utc),
                }
                
                token = jwt.encode(token_payload, self.secret_key, algorithm="HS256")
                
                # Create token record
                access_token = AccessToken(
                    token=token,
                    company_id=company_id,
                    status=AccessTokenStatus.ACTIVE,
                    settings={
                        "created_after_setup_payment": True,
                        "creation_date": datetime.now(timezone.utc).isoformat()
                    },
                    token_metadata={
                        "created_via": "company_setup",
                        "initial_creation": True
                    }
                )
                
                self.db.add(access_token)
                self.db.commit()
                
                await self.cache_token_info(access_token)

                logger.info(f"Created new access token for company {company_id}")
                return access_token
        
            except Exception as e:
                self.db.rollback()
                logger.error("token_creation_failed", 
                           company_id=company_id,
                           error=str(e),
                           exc_info=True)
                raise HTTPException(status_code=500, detail="Error creating access token")
    
    async def add_token_to_publisher(
        self,
        token: str,
        publisher_id: str,
        access_level: Dict = None
    ) -> bool:
        """ 
        Add token to publisher's whitelist
        """
        with LogOperation("add_token_to_publisher", token=token[:10], publisher_id=publisher_id):
            try:
                # Verify token exists and is active
                token_info = await self.get_cached_token_info(token)
                if not token_info:
                    logger.warning(f"Token {token[:10]}... not found or not active")
                    return False
                
                # Use pipeline for atomic operations
                with self.redis.pipeline() as pipe:
                    
                    # Add to publisher whitelist
                    whitelist_key = f"publisher:{publisher_id}:allowed_tokens"
                    pipe.sad(whitelist_key, token)
                    
                    # If we want to store additional access info per token
                    token_info_key = f"publisher:{publisher_id}:token:{token}"
                    access_data = {
                        "added_at": datetime.now(timezone.utc).isoformat(),
                        "access_level": access_level or {}
                    }
                    pipe.set(token_info_key, json.dumps(access_data))
                    
                    pipe.execute()
                    
                logger.info("token_added_to_publisher", 
                          publisher_id=publisher_id, 
                          token=token[:10])
                return True
            
            except RedisError as e:
                logger.error("redis_error_adding_token", 
                           publisher_id=publisher_id,
                           token=token[:10],
                           error=str(e),
                           exc_info=True)
                return False
            
            except Exception as e:
                logger.error("error_adding_token", 
                           publisher_id=publisher_id,
                           token=token[:10],
                           error=str(e),
                           exc_info=True)
                return False
    
    async def remove_token_from_publisher(
        self,
        publisher_id: str,
        token: str
    ) -> bool:
        """ 
        Remove token from publisher's whitelist
        """
        try:
            # Remove from whitelist and clean up token info
            pipe = self.redis.pipeline()
            pipe.srem(f"publisher:{publisher_id}:allowed_tokens", token)
            pipe.delete(f"publisher:{publisher_id}:token:{token}")
            pipe.execute()
            
            logger.info(f"Removed token from publisher {publisher_id} whitelist")
            return True

        except Exception as e:
            logger.error(f"Error removing token from publisher whitelist: {str(e)}")
            return False
    
    async def validate_token_for_publisher(
        self,
        publisher_id: str,
        token: str,
        request_metadata: Optional[Dict] = None
    ) -> bool:
        """ 
        Validate if token is in publisher's whitelist
        """
        with LogOperation("validate_token", publisher_id=publisher_id, token=token[:10]):
            try:
                # Check if token exists in publisher's whitelist
                whitelist_key = f"publisher:{publisher_id}:allowed_tokens"
                if not self.redis.sismember(whitelist_key, token):
                    logger.warning("token_not_in_whitelist", 
                                 publisher_id=publisher_id, 
                                 token=token[:10])
                    return False
                
                if not await self.check_rate_limits_redis(token, publisher_id):
                    logger.warning("rate_limits_exceeded", 
                                 publisher_id=publisher_id, 
                                 token=token[:10])
                    return False
                
                # Verify token is still active
                token_info = await self.get_cached_token_info(token)
                if not token_info:
                    logger.warning("token_info_not_found", 
                                 publisher_id=publisher_id, 
                                 token=token[:10])
                    return False
                
                # Record usage
                await self.record_usage(token, publisher_id, request_metadata)
                
                return True
            
            except Exception as e:
                logger.error("token_validation_error",
                           publisher_id=publisher_id,
                           token=token[:10],
                           error=str(e),
                           exc_info=True)
                return False

    async def cache_token_info(self, token: AccessToken) -> None:
        """Cache basic token information in Redis"""
        try:
            token_key = f"token_info:{token.token}"
            token_data = {
                "id": str(token.id),
                "company_id": str(token.company_id),
                "status": token.status.value,
                "created_at": token.created_at.isoformat()
            }

            self.redis.set(
                token_key,
                json.dumps(token_data),
                ex=30 * 24 * 60 * 60  # 30 days
            )
        
        except RedisError as e:
            logger.error(f"Redis error caching token info: {str(e)}")
        except Exception as e:
            logger.error(f"Error caching token info: {str(e)}")
    
    async def get_cached_token_info(self, token: str) -> Optional[Dict]:
        """Get token information from Redis cache"""
        try:
            token_key = f"token_info:{token}"
            token_data = self.redis.get(token_key)
            return json.loads(token_data) if token_data else None
        except Exception as e:
            logger.error(f"Error getting cached token info: {str(e)}")
            return None
    
    async def check_rate_limits_redis(
        self,
        token: str,
        publisher_id: str
    ) -> bool:
        """Check rate limits using Redis for better performance"""
        try:
            now = datetime.now(timezone.utc)
            
            with self.redis.pipeline() as pipe:
                
                # Keys for different time windows
                minute_key = f"rate_limits:{token}:{publisher_id}:minute:{now.strftime('%Y%m%d%H%M')}"
                daily_key = f"rate_limits:{token}:{publisher_id}:daily:{now.strftime('%Y%m%d')}"
                monthly_key = f"rate_limits:{token}:{publisher_id}:monthly:{now.strftime('%Y%m')}"

                # Increment counters and get values
                pipe.incr(minute_key)
                pipe.expire(minute_key, 60)  # Expire after 1 minute
                
                pipe.incr(daily_key)
                pipe.expire(daily_key, 86400)  # Expire after 1 day
                
                pipe.incr(monthly_key)
                pipe.expire(monthly_key, 2592000)  # Expire after 30 days
                
                results = pipe.execute()
            
            minute_count, _, daily_count, _, monthly_count, _ = results

            # Get limits from token info
            token_info = await self.get_cached_token_info(token)
            rate_limits = token_info.get('rate_limits', {})

            # Check against limits
            if minute_count > rate_limits.get('per_minute', 60):
                logger.warning(f"Rate limit exceeded for token {token[:10]}...")
                return False

            if daily_count > rate_limits.get('per_day', 5000):
                logger.warning(f"Daily limit exceeded for token {token[:10]}...")
                return False

            if monthly_count > rate_limits.get('per_month', 100000):
                logger.warning(f"Monthly limit exceeded for token {token[:10]}...")
                return False

            return True

        except RedisError as e:
            logger.error(f"Redis error checking rate limits: {str(e)}")
            return True  # Default to allowing on error
        
        except Exception as e:
            logger.error(f"Error checking rate limits: {str(e)}")
            return True  # Default to allowing on error
    
    async def record_usage(
        self,
        token: str,
        publisher_id: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """ 
        Record access token usage for analytics and billing
        """
        with LogOperation("record_usage", token=token[:10], publisher_id=publisher_id):
            try:
                
                # Get token record
                token_record = self.db.query(AccessToken).filter(
                    AccessToken.token == token
                ).first()
                
                if not token_record:
                    logger.error("token_record_not_found", token=token[:10])
                    return
                
                usage = APIUsageRecord(
                    access_token_id=token_record.id,
                    publisher_id=publisher_id,
                    ip_address=metadata.get('ip_address'),
                    user_agent=metadata.get('user_agent'),
                    request_path=metadata.get('path'),
                    ai_tokens_processed=metadata.get('ai_tokens_processed', 0),
                    content_type=metadata.get('content_type'),
                    content_size_bytes=metadata.get('content_size_bytes'),
                    usage_metadata=metadata or {}
                )
                
                self.db.add(usage)
                token_record.total_api_requests += 1
                token_record.total_ai_tokens_processed += metadata.get('ai_tokens_processed', 0)

                self.db.commit()
                
                logger.info("usage_recorded",
                          token_id=str(token_record.id),
                          publisher_id=publisher_id,
                          tokens_processed=metadata.get('ai_tokens_processed', 0))

            except Exception as e:
                self.db.rollback()
                logger.error("usage_recording_failed",
                           token=token[:10],
                           publisher_id=publisher_id,
                           error=str(e),
                           exc_info=True)
    
    async def revoke_token(self, token_id: str) -> bool:
        """Revoke access token and remove from all publisher whitelists"""
        with LogOperation("revoke_token", token_id=token_id):
            try:
                token = self.db.query(AccessToken).filter(
                    AccessToken.id == token_id
                ).first()
                
                if not token:
                    logger.warning("token_not_found", token_id=token_id)
                    return False

                # Update database status
                token.status = AccessTokenStatus.REVOKED
                token.revoked_at = datetime.now(timezone.utc)
                self.db.commit()

                # Remove from all publisher whitelists
                pattern = "publisher:*:allowed_tokens"
                for key in self.redis.scan_iter(pattern):
                    self.redis.srem(key, token.token)

                # Update cached token info
                token_key = f"token_info:{token.token}"
                self.redis.delete(token_key)
                
                logger.info("token_revoked", 
                          token_id=token_id, 
                          token=token.token[:10])
                return True

            except Exception as e:
                self.db.rollback()
                logger.error("token_revocation_failed",
                           token_id=token_id,
                           error=str(e),
                           exc_info=True)
                return False
    
    async def get_token_usage(
        self,
        token_id: str,
        publisher_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[APIUsageRecord]:
        """Get usage history for a token, optionally filtered by publisher"""
        try:
            query = self.db.query(APIUsageRecord).filter(
                APIUsageRecord.access_token_id == token_id
            )
            
            if publisher_id:
                query = query.filter(APIUsageRecord.publisher_id == publisher_id)
            
            if start_date:
                query = query.filter(APIUsageRecord.timestamp >= start_date)
            if end_date:
                query = query.filter(APIUsageRecord.timestamp <= end_date)
                
            return query.order_by(APIUsageRecord.timestamp.desc()).all()

        except Exception as e:
            logger.error(f"Error getting token usage: {str(e)}")
            return []
        
    def __del__(self):
        """Cleanup when the AccessTokenService is destroyed"""
        RedisClientFactory.close_connection()