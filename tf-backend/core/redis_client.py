# tf-backend/core/redis_client.py

import redis
from redis.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, TimeoutError
import logging
from core.config import get_settings
from typing import Optional

logger = logging.getLogger(__name__)

class RedisClientFactory:
    _instance: Optional[redis.Redis] = None
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        """
        Get or create a Redis client instance using the Singleton pattern
        """
        if cls._instance is None:
            settings = get_settings()
            connection_params = settings.get_redis_connection_params()
            
            # Configure retry strategy
            retry = Retry(
                ExponentialBackoff(),
                3  # maximum number of retries
            )
            
            try:
                cls._instance = redis.Redis(
                    **connection_params,
                    retry=retry,
                    decode_responses=True  # Automatically decode responses to strings
                )
                
                # Test connection
                cls._instance.ping()
                logger.info("Successfully connected to Redis")
                
            except (ConnectionError, TimeoutError) as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")
                raise
            
        return cls._instance
    
    @classmethod
    def close_connection(cls):
        """
        Close the Redis connection if it exists
        """
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None