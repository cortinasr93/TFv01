# tf-backend/api/token_metering/services.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
import logging
from bs4 import BeautifulSoup
import tiktoken
from core.models.payment import UsageRecord, UsageType
from api.access_tokens.services import AccessTokenService
from core.logging_config import get_logger, LogOperation

logger = get_logger(__name__)

class TokenMeteringService:
    def __init__(self, db: Session):
        self.db = db
        self.access_token_service = AccessTokenService(db)
        
        # Initialize tokenizer - cache as instance variable for reuse
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4o")
            logger.info("tokenizer_initialized", model="gpt-4")
        except Exception as e:
            logger.error("tokenizer_initialization_failed", error=str(e), exc_info=True)
            raise
        
        self.RATE_PER_TOKEN = 0.0002 # $0.20 per 1000 tokens
        self.PLATFORM_FEE_PERCENTAGE = 0.03 # 3% platform fee
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        with LogOperation("count_tokens", text_length=len(text)):
            try:
                token_count = len(self.tokenizer.encode(text))
                logger.debug("tokens_counted", 
                           token_count=token_count, 
                           text_length=len(text))
                return token_count
            except Exception as e:
                logger.error("token_counting_failed", 
                           error=str(e), 
                           text_length=len(text))
                # Return approximate count as fallback (1 token ≈ 4 characters)
                return len(text) // 4
    
    async def process_bot_request(
        self,
        token: str,
        publisher_id: str,
        content: str,
        request_metadata: Optional[Dict] = None
    ) -> Dict:
        """Process a bot request and track content usage

        Args:
            token (str): Access token from AI comany
            publisher_id (str): ID of publisher being accessed
            content (str): content being accessed
            request_metadata (Optional[Dict], optional): Additional request info (IP, user agent, etc.). Defaults to None.

        Returns:
            Dict: Contains access results and usage info
        """
        with LogOperation("process_bot_request", 
                        token=token[:10], 
                        publisher_id=publisher_id):
            try:
                # validate token
                is_valid = await self.access_token_service.validate_token_for_publisher(
                    publisher_id=publisher_id,
                    token=token,
                    request_metadata=request_metadata                
                )
                
                if not is_valid:
                    logger.warning("token_validation_failed", 
                                 token=token[:10], 
                                 publisher_id=publisher_id)
                    
                    return {
                        'allowed': False,
                        'reason': 'Invalid token or access denied'
                    }
                
                token_record = await self.access_token_service.get_cached_token_info(token)
                if not token_record:
                    logger.warning("token_record_not_found", token=token[:10])
                    
                    return {
                        'allowed': False,
                        'reason': 'Access Token not found'
                    }
                
                # Analyze content and calcualte costs
                content_analysis = await self.analyze_content(content)
                token_count = content_analysis['token_count']
                
                # Calculate costs
                raw_amount = token_count * self.RATE_PER_TOKEN
                platform_fee = raw_amount * self.PLATFORM_FEE_PERCENTAGE
                publisher_amount = raw_amount - platform_fee
                
                # Create usage record with token count
                usage_record = UsageRecord(
                    company_id=token_record['company_id'],
                    publisher_id=publisher_id,
                    usage_type=UsageType.RAG,  # or TRAINING based on metadata
                    num_tokens=token_count,
                    token_rate=self.RATE_PER_TOKEN,
                    raw_amount=raw_amount,
                    platform_fee=platform_fee,
                    publisher_amount=publisher_amount,
                    total_cost=raw_amount,
                    usage_metadata={
                        'content_type': content_analysis['content_type'],
                        'content_size': content_analysis['content_size_bytes'],
                        'request_info': request_metadata or {}
                    }
                )
                
                self.db.add(usage_record)
                self.db.commit()
                
                logger.info("usage_recorded",
                          token=token[:10],
                          publisher_id=publisher_id,
                          company_id=token_record['company_id'],
                          token_count=token_count,
                          amount=raw_amount,
                          usage_id=str(usage_record.id))
                
                return {
                    'allowed': True,
                    'usage_id': str(usage_record.id),
                    'tokens_processed': token_count,
                    'cost': raw_amount,
                    'content_analysis': content_analysis
                }
                
            except Exception as e:
                self.db.rollback()
                logger.error("bot_request_processing_failed",
                           token=token[:10],
                           publisher_id=publisher_id,
                           error=str(e),
                           exc_info=True)
                return {
                    'allowed': False,
                    'reason': 'Internal processing error'
                }
            
    async def analyze_content(self, content: str) -> Dict:
        """
        Analyze content to extract metadata and count tokens

        Args:
            content (str): raw content to analyze

        Returns:
            Dict: Contains analysis results (token count, size, type)
        """
        with LogOperation("analyze_content", content_length=len(content)):

            try:
                clean_content, content_type = self.clean_and_type_content(content)
                token_count = self.count_tokens(clean_content)
                
                analysis_results = {
                    'token_count': token_count,
                    'content_size_bytes': len(content.encode('utf-8')),
                    'content_type': content_type,
                    'estimated_cost': token_count * self.RATE_PER_TOKEN
                }
                
                logger.info("content_analyzed",
                           token_count=token_count,
                           content_type=content_type,
                           size_bytes=analysis_results['content_size_bytes'])
                
                return analysis_results
            
            except Exception as e:
                logger.error("content_analysis_failed",
                           error=str(e),
                           content_length=len(content),
                           exc_info=True)
                raise
    
    def clean_and_type_content(self, content: str) -> Tuple[str, str]:
        """
        Clean content and determine type

        Args:
            content (str): raw content

        Returns:
            Tuple[str, str]: Tuple of (cleaned_content, content_type)
        """
        with LogOperation("clean_and_type_content", content_length=len(content)):
            try:
                # Check if content is HTML
                if '<html' in content.lower() or '<body' in content.lower():
                    try:
                        soup = BeautifulSoup(content, 'html.parser')
                        # Remove non-content elements
                        for tag in soup(['script', 'style', 'meta', 'link', 'noscript', 'iframe']):
                            tag.decompose()
                        
                        # Get text preserving some structure
                        content = ' '.join([
                            (tag.get_text(strip=True) + '. ')
                            for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
                            if tag.get_text(strip=True)
                        ])
                        logger.debug("html_content_cleaned",
                                   original_length=len(content),
                                   cleaned_length=len(content))
                        
                        return content.strip(), 'text/html'
                    except Exception as e:
                        logger.error("html_cleaning_failed",
                                   error=str(e),
                                   exc_info=True)
                        # Fallback to raw content
                        return content, 'text/html'
                
                # Basic content type detection
                if content.startswith('{') and content.endswith('}'):
                    return content, 'application/json'
                elif '<xml' in content.lower() or '<?xml' in content:
                    return content, 'application/xml'
                else:
                    return content, 'text/plain'
                
            except Exception as e:
                logger.error("content_cleaning_failed",
                           error=str(e),
                           exc_info=True)
                return content, 'text/plain'
    
    async def get_usage_analytics(
        self,
        company_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get usage analytics for an AI company
        
        Args:
            company_id: ID of AI company
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            Dict containing usage statistics and trends
        """
        try:
            query = self.db.query(UsageRecord).filter(
                UsageRecord.company_id == company_id
            )
            
            if start_date:
                query = query.filter(UsageRecord.created_at >= start_date)
            if end_date:
                query = query.filter(UsageRecord.created_at <= end_date)

            records = query.all()
            
            return {
                'total_tokens': sum(r.num_tokens for r in records),
                'total_cost': sum(r.total_cost for r in records),
                'total_requests': len(records),
                'average_tokens_per_request': sum(r.num_tokens for r in records) / len(records) if records else 0,
                'publishers_accessed': len(set(r.publisher_id for r in records))
            }
        except Exception as e:
            logger.error(f"Error getting usage analytics: {str(e)}")
            raise