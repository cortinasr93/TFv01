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

logger = logging.getLogger(__name__)

class TokenMeteringService:
    def __init__(self, db: Session):
        self.db = db
        self.access_token_service = AccessTokenService(db)
        
        # Initialize tokenizer - cache as instance variable for reuse
        self.tokenizer = tiktoken.encoding_for_model("gpt-4o")
        self.RATE_PER_TOKEN = 0.0002 # $0.20 per 1000 tokens
        self.PLATFORM_FEE_PERCENTAGE = 0.03 # 3% platform fee
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        
        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens: {str(e)}")
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
        try:
            # validate token
            is_valid = await self.access_token_service.validate_token_for_publisher(
                publisher_id=publisher_id,
                token=token,
                request_metadata=request_metadata                
            )
            
            if not is_valid:
                return {
                    'allowed': False,
                    'reason': 'Invalid token or access denied'
                }
            
            token_record = await self.access_token_service.get_cached_token_info(token)
            if not token_record:
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
            
            return {
                'allowed': True,
                'usage_id': str(usage_record.id),
                'tokens_processed': token_count,
                'cost': raw_amount,
                'content_analysis': content_analysis
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing bot request: {str(e)}")
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
        try:
            clean_content, content_type = self.clean_and_type_content(content)
            token_count = self.count_tokens(clean_content)
            
            return {
                'token_count': token_count,
                'content_size_bytes': len(content.encode('utf-8')),
                'content_type': content_type,
                'estimated_cost': token_count * self.RATE_PER_TOKEN
            }
        
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            raise
    
    def clean_and_type_content(self, content: str) -> Tuple[str, str]:
        """
        Clean content and determine type

        Args:
            content (str): raw content

        Returns:
            Tuple[str, str]: Tuple of (cleaned_content, content_type)
        """
        
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
                return content.strip(), 'text/html'
            except Exception as e:
                logger.error(f"Error parsing HTML content: {str(e)}")
                # Fallback to raw content
                return content, 'text/html'
        
        # Basic content type detection
        if content.startswith('{') and content.endswith('}'):
            return content, 'application/json'
        elif '<xml' in content.lower() or '<?xml' in content:
            return content, 'application/xml'
        else:
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