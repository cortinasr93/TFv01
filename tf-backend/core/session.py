# tf-backend/core/session.py

import json
import uuid
import logging
from datetime import datetime, timedelta
from core.redis_client import RedisClientFactory
from redis.exceptions import RedisError
from typing import Optional, Dict
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class SessionManager:
    def __init__(self):
        try:
            self.redis = RedisClientFactory.get_client()
            self.session_duration = 1800 # session ends after 30 mins
            
            # Test connection
            pong = self.redis.ping()
            logger.info(f"Session Manager Redis connection test: {pong}")
            
        except RedisError as e:
            logger.error(f"Redis connection failed in SessionManager: {str(e)}")
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
        session_key = f"{{sess}}:session:{session_id}"
        
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
            with self.redis.pipeline() as pipe:
                pipe.setex(
                    session_key,
                    self.session_duration,
                    json.dumps(session_data)
                )
                
                # Add to user's sessions set
                user_sessions_key= f"{{sess}}:user:{user_data['id']}:sessions"
                pipe.sadd(user_sessions_key, session_id)
                pipe.expire(user_sessions_key, self.session_duration)
                
                pipe.execute()
                
            logger.info(f"Session created: {session_key}")
            return session_id
                
        except RedisError as e:
            logger.error(f"Redis error creating session: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating session: {str(e)}")
            raise
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """ 
        Retrieve and validate a session
        """
        session_key = f"{{sess}}:session:{session_id}"
        logger.info(f"Looking up session: {session_key}")
        
        try: 
            session_data = self.redis.get(session_key)
            
            if not session_data:
                return None
            
            session = json.loads(session_data)
            
            # Update last activity and extend session using pipeline
            with self.redis.pipeline() as pipe:
                session["last_activity"] = datetime.now().isoformat()
                pipe.setex(
                    session_key,
                    self.session_duration,
                    json.dumps(session)
                )
                # Also extend user sessions set expiry
                user_sessions_key = f"{{sess}}:user:{session['user_id']}:sessions"
                pipe.expire(user_sessions_key, self.session_duration)
                
                pipe.execute()
                
            return session
        
        except RedisError as e:
            logger.error(f"Redis error getting session: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error processing session: {str(e)}")
            return None
    
    def end_session(self, session_id: str) -> bool:
        """ 
        End a user session
        """
        try:
            session_key = f"{{sess}}:session:{session_id}"
            
            # Get session first to get user_id
            session_data = self.redis.get(session_key)
            if session_data:
                session = json.loads(session_data)
                user_id = session.get("user_id")
                
                if user_id:
                    # Remove session and update user's sessions set atomically
                    with self.redis.pipeline() as pipe:
                        pipe.delete(session_key)
                        pipe.srem(f"{{sess}}:user:{user_id}:sessions", session_id)
                        pipe.execute()
                        return True
        
            return False
        
        except RedisError as e:
            logger.error(f"Redis error ending session: {str(e)}")
            return False
    
    def get_user_sessions(self, user_id: str) -> list:
        """ 
        Get all active sessions for a user
        """
        try:
            user_sessions_key = f"{{sess}}:user:{user_id}:sessions"
            sessions = []
            
            # Get all session IDs for this user from their set
            session_ids = self.redis.smembers(user_sessions_key)
            
            if not session_ids:
                return []
            
            # Use pipeline to get all sessions in one round trip
            with self.redis.pipeline() as pipe:
                # Queue up all the session gets
                for session_id in session_ids:
                    pipe.get(f"{{sess}}:session:{session_id}")
                
                # Execute pipeline and process results
                results = pipe.execute()
                
                for session_id, data in zip(session_ids, results):
                    if data:  # If session exists
                        try:
                            session = json.loads(data)
                            sessions.append({
                                "session_id": session_id,
                                **session
                            })
                        except json.JSONDecodeError:
                            logger.error(f"Invalid session data for session {session_id}")
                            # Clean up invalid session
                            self.redis.srem(user_sessions_key, session_id)
                    else:
                        # Session was expired/deleted, remove from user's set
                        self.redis.srem(user_sessions_key, session_id)
            
            return sessions
            
        except RedisError as e:
            logger.error(f"Redis error getting user sessions: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting user sessions: {str(e)}")
            return []
    
    def cleanup_expired_sessions(self):
        """
        Cleanup any expired sessions
        """
        try:
            pattern = f"{{sess}}:session:*"
            for key in self.redis.scan_iter(pattern):
                if self.redis.ttl(key) <= 0:
                    self.redis.delete(key)
        
        except RedisError as e:
            logger.error(f"Redis error during session cleanup: {str(e)}")
    
    def __del__(self):
        """Cleanup when the SessionManager is destroyed"""
        RedisClientFactory.close_connection()