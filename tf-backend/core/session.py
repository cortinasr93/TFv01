# tf-backend/core/session.py

import json
import uuid
import logging
from datetime import datetime, timedelta
import redis
from typing import Optional, Dict
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class SessionManager:
    def __init__(self):
        try:
            logger.info(f"Connecting to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")

            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
        
            self.session_duration = 1800 # session ends after 30 mins
            
            # Test connection
            pong = self.redis.ping()
            logger.info(f"Redis ping response: {pong}")
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            raise
    
    def create_session(self, user_data: Dict) -> str:
        """ 
        Create a new session for a user
        """
        logger.debug(f"user_data passed to create_session: {user_data}")
        
        # Validate required fields in user_data
        required_keys = ["id", "email", "user_type"]
        for key in required_keys:
            if key not in user_data:
                logger.error(f"Missing required key '{key}' in user_data: {user_data}")
                raise ValueError(f"Missing required key '{key}' in user_data")

        session_id = str(uuid.uuid4())
        session_key = f"session:{session_id}"
        
        session_data = {
            "user_id": str(user_data["id"]),
            "email": user_data["email"],
            "user_type": user_data["user_type"],
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
        }       
        
        if not session_data["user_id"] or not session_data["email"]:
            raise ValueError("Missing required user data for session creation.")
        
        # Store session in Redis with expiration
        try:
            self.redis.setex(
                session_key,
                self.session_duration,
                json.dumps(session_data)
            )
            logger.info(f"Session created: {session_key}")
            
            # Verify session was stored
            stored_data = self.redis.get(session_key)
            logger.info(f"Session verification: {'success' if stored_data else 'failed'}")
            
            return session_id
             
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """ 
        Retrieve and validate a session
        """
        session_key = f"session:{session_id}"
        logger.info(f"Looking up session: {session_key}")
        
        session_data = self.redis.get(session_key)
        logger.info(f"Session data found: {bool(session_data)}")
        
        if not session_data:
            return None
        
        try:
        
            session = json.loads(session_data)
            logger.info(f"Session loaded for user: {session.get('email')}")
            
            # Update last activity and extend session
            session["last_activity"] = datetime.now().isoformat()
            self.redis.setex(
                session_key,
                self.session_duration,
                json.dumps(session)
            )
        
            return session
        
        except Exception as e:
            logger.error(f"Error processing session: {str(e)}. \nRaw data:{session_data}")
            return None
    
    def end_session(self, session_id: str) -> bool:
        """ 
        End a user session
        """
        return bool(self.redis.delete(f"session:{session_id}"))
    
    def get_user_sessions(self, user_id: str) -> list:
        """ 
        Get all active sessions for a user
        """
        pattern = f"session:*"
        sessions = []
        
        for key in self.redis.scan_iter(pattern):
            data = self.redis.get(key)
            if data:
                session = json.loads(data)
                if session.get("user_id") == str(user_id):
                    sessions.append({
                        "session_id": key.split(":")[1],
                        **session
                    })
        
        return sessions
    
    def cleanup_expired_sessions(self):
        """
        Cleanup any expired sessions
        """
        pattern = f"session:*"
        for key in self.redis.scan_iter(pattern):
            if self.redis.ttl(key) <= 0:
                self.redis.delete(key)