# tf-backend/api/detection/services.py

from fastapi import Request
from sqlalchemy.orm import Session
import redis
import json
import logging
from typing import Dict
from datetime import datetime, timezone
from .utils import UserAgentAnalyzer, BROWSER_HEADERS
from core.config import get_settings
from core.models.detection import RequestLog

logger = logging.getLogger(__name__)

class BotDetectorService:
    def __init__(self, db: Session):
        self.db = db
        settings = get_settings()
        
        self.ua_analyzer = UserAgentAnalyzer()
        self.BROWSER_HEADERS = BROWSER_HEADERS
        
        # Initialize Redis client
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
    
        self.KNOWN_BOT_PATTERNS = {
        
            # AI Company Crawlers
            'anthropic-ai': {
                'company': 'Anthropic',
                'type': 'AI Training',
                'confidence': 1.0
            },
            'claude-web': {
                'company': 'Anthropic',
                'type': 'AI Training',
                'confidence': 1.0
            },
            'chatgpt-user': {
                'company': 'OpenAI',
                'type': 'AI Training',
                'confidence': 1.0
            },
            'gptbot': {
                'company': 'OpenAI',
                'type': 'AI Training',
                'confidence': 1.0
            },
            'cohere-ai': {
                'company': 'Cohere',
                'type': 'AI Training',
                'confidence': 1.0
            },
            'perplexitybot': {
                'company': 'Perplexity',
                'type': 'AI Training',
                'confidence': 1.0
            },
            'ccbot': {
                'company': 'Common Crawl',
                'type': 'AI Training',
                'confidence': 1.0
            },
            'bytespider': {
                'company': 'ByteDance',
                'type': 'AI Training',
                'confidence': 1.0
            },
            'applebot-extended': {
                'company': 'Apple',
                'type': 'AI Training',
                'confidence': 1.0
            },
            'diffbot': {
                'company': 'Diffbot',
                'type': 'AI Training',
                'confidence': 1.0
            },
            'imagesiftbot': {
                'company': 'ImageSift',
                'type': 'AI Training',
                'confidence': 1.0
            },
            'webz.io': {
                'company': 'Webz.io',
                'type': 'AI Training',
                'confidence': 1.0
            },
            
            # Search Engine and Social Media Crawlers
            'googlebot': {
                'company': 'Google',
                'type': 'Search Engine',
                'confidence': 1.0
            },
            'google-extended': {
                'company': 'Google',
                'type': 'Search Engine',
                'confidence': 1.0
            },
            'googleother': {
                'company': 'Google',
                'type': 'Search Engine',
                'confidence': 1.0
            },
            'bingbot': {
                'company': 'Microsoft',
                'type': 'Search Engine',
                'confidence': 1.0
            },
            'facebookbot': {
                'company': 'Meta',
                'type': 'Social Media',
                'confidence': 1.0
            },
            
            # Generic Patterns (lower confidence as they might be false positives)
            'crawl': {
                'company': 'Unknown',
                'type': 'Generic Crawler',
                'confidence': 0.7
            },
            'spider': {
                'company': 'Unknown',
                'type': 'Generic Spider',
                'confidence': 0.7
            },
            'bot': {
                'company': 'Unknown',
                'type': 'Generic Bot',
                'confidence': 0.6
            }
        }
        
        self.BROWSER_HEADERS = [
            'accept-language',
            'accept-encoding',
            'sec-fetch-dest',
            'sec-fetch-mode',
            'sec-fetch-site',
            'sec-ch-ua'
        ]
    
    async def analyze_request(self, request: Request, publisher_id: str) -> Dict:
        """ 
        Analyze a request using multiple detection methods
        Returns detection results with confidence score
        """
        detection_results = {
            'is_bot': False,
            'confidence_score': 0.0,
            'detection_methods': [],
            'bot_name': None,
            'bot_type': None,
            'is_ai_crawler': False,
            'client_info': None
        }
        
        # Get request details
        ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        headers = dict(request.headers)
        
        # UA analysis
        client_info = self.ua_analyzer.analyze_user_agent(user_agent)
        detection_results['client_info'] = client_info
        
        if client_info['is_bot']:
            detection_results['is_bot'] = True
            detection_results['confidence_score'] = max(detection_results['confidence_score'], 0.8)
            detection_results['detection_methods'].append('us_parser')
            if detection_results['bot_type'] is None:
                detection_results['bot_type'] = 'Generic Bot'
        
        # 1. Check known patterns
        await self._check_known_patterns(user_agent, detection_results)
        
        # 2. Analyze browser fingerprint
        await self._analyze_browser_fingerprint(headers, detection_results, client_info)
        
        # 3. Check request patterns
        await self._analyze_request_patterns(ip, publisher_id, detection_results)
        
        # 4. Check IP reputation
        await self._check_ip_reputation(ip, detection_results)
        
        # 5. Update detection history
        await self._update_detection_history(request, ip, publisher_id, detection_results)
        
        if not detection_results['is_bot']:
            return detection_results
        
        if len(detection_results['detection_methods']) < 2 or detection_results['confidence_score'] < 0.8:
            detection_results['is_bot'] = False
            detection_results['confidence_score'] = 0.0
            detection_results['detection_methods'] = []
        
        if detection_results['is_bot']:
            logger.info(f"Request detected as bot with methods: {detection_results['detection_methods']}")
            logger.info(f"Headers present: {headers}")
            logger.info(f"Client info: {client_info}")
        
        return detection_results
    
    async def _check_known_patterns(self, user_agent: str, results: Dict):
        """
        Checks user agent against known bot patterns
        """
        
        ua_lower = user_agent.lower()
        
        for pattern, info in self.KNOWN_BOT_PATTERNS.items():
            if pattern in ua_lower:
                results['is_bot'] = True
                results['confidence_score'] = max(results['confidence_score'], info['confidence'])
                results['detection_methods'].append('known_pattern')
                results['bot_name'] = info['company']
                results['bot_type'] = info['type']
                
                if info['type'] == 'AI Training':
                    results['is_ai_crawler'] = True
                    results['detection_methods'].append('ai_crawler')
                
                logger.info(f"Bot detected: {info['company']} ({info['type']}) - "
                          f"Confidence: {info['confidence']}")

                return
    
    async def _analyze_browser_fingerprint(self, headers: Dict, results: Dict, client_info: Dict):
        """
        Analyze browser fingerprint for bot-like characteristics
        """
        # Check if this is an API call vs browser request
        is_api_call = headers.get('content-type') == 'application/json'
        
        if not is_api_call:
        
            missing_headers = [header for header in self.BROWSER_HEADERS
                            if header not in headers]
            
            if len(missing_headers) >= 5:
                results['is_bot'] = True
                results['confidence_score'] = max(results['confidence_score'], 0.7)
                results['detection_methods'].append('browser_fingerprint')
        
        if client_info['is_mobile']:
            if 'sec-ch-ua-mobile' in headers and headers['sec-ch-ua-mobile'] != '?1':
                results['confidence_score'] = max(results['confidence_score'], 0.8)
                results['detection_methods'].append('mobile_mismatch')
    
    async def _analyze_request_patterns(self, ip: str, publisher_id: str, results: Dict):
        """
        Analyze request patterns for bot-like behavior
        """
        key = f"requests:{publisher_id}:{ip}"
        recent_requests = self.redis.lrange(key, 0, 99) # last 100 requests
        timestamps = []
        
        if recent_requests:
            for req in recent_requests:
                try:
                    req_data = json.loads(req)
                    timestamps.append(float(req_data['timestamp']))
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
        
        # Only analyze if we have enough timestamps
        if len(timestamps) >=10:
            time_diff = max(timestamps) - min(timestamps)
            if time_diff > 0:
                requests_per_second = len(timestamps) / time_diff
                
                if requests_per_second > 10:
                    results['is_bot'] = True
                    results['confidence_score'] = max(results['confidence_score'], 0.8)
                    results['detection_methods'].append('high_frequency')

                intervals = [timestamps[i] - timestamps[i-1]
                             for i in range(1, len(timestamps))]
                
                if len(set(intervals)) == 1: # i.e., all intervals are identical
                    results['is_bot'] = True
                    results['confidence_score'] = max(results['confidence_score'], 0.9)
                    results['detection_methods'].append('consistent_timing')
                    
    async def _check_ip_reputation(self, ip: str, results: Dict):
        """
        Check IP reputation from Redis
        """
        reputation_key = f"ip_reputation:{ip}"
        reputation = self.redis.get(reputation_key)
        
        if reputation:
            try:
                reputation_data = json.loads(reputation)
                reputation_score = float(reputation_data.get('score', 1.0))
                
                if reputation_score < 0.5:
                    results['is_bot'] = True
                    results['confidence_score'] = max(results['confidence_score'], 0.7)
                    results['detection_methods'].append('ip_reputation')
            
            except (json.JSONDecodeError, ValueError):
                pass
            
    async def _update_detection_history(self, request: Request, ip: str, publisher_id: str, results: Dict):
        """
        Update detection history in Redis and PostgreSQL
        """
        # Update Redis request history
        request_data = {
            'timestamp': datetime.now(timezone.utc).timestamp(),
            'path': str(request.url.path),
            'method': request.method,
            'is_bot': results.get('is_bot', False),
            'confidence': results.get('confidence_score', 0.0)
        }
        
        key = f"requests:{publisher_id}:{ip}"
        self.redis.lpush(key, json.dumps(request_data))
        self.redis.ltrim(key, 0, 99) # Keep last 100 requests
        self.redis.expire(key, 3600) #expire after 1 hour
        
        # Update IP reputation if bot detected with high confidence
        if results.get('is_bot', False) and results.get('confidence_score', 0.0) > 0.8:
            reputation_key = f"ip_reputation:{ip}"
            reputation_data = {
                'score': 0.3, # Lower score = suspicious IP
                'last_updated': datetime.now(timezone.utc).timestamp(),
                'detection_methods': results.get('detection_methods', [])
            }
            self.redis.set(
                reputation_key,
                json.dumps(reputation_data),
                ex=86400
            )
        
        # Log to Postgres
        log_entry = RequestLog(
            ip_address=ip,
            user_agent=request.headers.get("user-agent", ""),
            request_path=str(request.url.path),
            request_method=request.method,
            is_bot=results.get('is_bot', False),
            is_ai_crawler=results.get('is_ai_crawler', False),
            bot_name=results.get('bot_name'),
            bot_type=results.get('bot_type'),
            confidence_score=results.get('confidence_score', 0.0),
            detection_methods=json.dumps(results.get('detection_methods', [])),
            publisher_id=publisher_id
        )
        
        try:
            self.db.add(log_entry)
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to log request: {e}")
            self.db.rollback()

    async def get_detection_stats(self, publisher_id: str) -> Dict:
        """Get detection statistics for a publisher."""
        # Implementation for getting detection stats
        pass
    
    async def get_ip_reputation(self, ip_address: str) -> Dict:
        """Get reputation data for an IP address."""
        reputation_key = f"ip_reputation:{ip_address}"
        reputation = self.redis.get(reputation_key)
        
        if reputation:
            try:
                return json.loads(reputation)
            except json.JSONDecodeError:
                return {"score": 1.0}  # Default good reputation
        
        return {"score": 1.0}  # Default good reputation