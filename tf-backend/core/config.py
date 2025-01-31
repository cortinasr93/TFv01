# tf-backend/core/config.py

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache
from typing import Optional
from dotenv import load_dotenv
import os
import secrets

load_dotenv()

class Settings(BaseSettings):
    model_config = ConfigDict(
        case_sensitive = True,
        env_file = ".env"
    )
    
    # API backend URL
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    API_URL: str = BASE_URL
    
    # Frontend Application URL
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # AWS RDS PostgreSQL settings
    DB_HOST: str = os.getenv("DB_HOST", "trainfair-db.crsew4uugrsd.us-east-2.rds.amazonaws.com")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "trainfair")
    DB_USER: str = os.getenv("DB_USER", "trainfair_app")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Redis AWS ElastiCache Settings
    # REDIS_PRIMARY_ENDPOINT: str = os.getenv("REDIS_PRIMARY_ENDPOINT", "localhost")
    # REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    # REDIS_SSL: bool = os.getenv("REDIS_SSL", "false").lower() == "true"
    # REDIS_AUTH_TOKEN: Optional[str] = os.getenv("REDIS_AUTH_TOKEN")  # For auth if using Redis AUTH
    # REDIS_USER: Optional[str] = os.getenv("REDIS_USER")  # For Redis ACLs if used
    # REDIS_TLS_CERT_PATH: Optional[str] = os.getenv("REDIS_TLS_CERT_PATH")  # For SSL/TLS
    
    # Basic Redis connection settings
    REDIS_CONNECTION_TIMEOUT: int = 5
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_RETRY_ON_TIMEOUT: bool = True
    REDIS_MAX_CONNECTIONS: int = 10
    
    # Helper method to get Redis connection parameters
    def get_redis_connection_params(self) -> dict:
        params = {
            'host': self.REDIS_HOST,
            'port': self.REDIS_PORT,
            'password': self.REDIS_PASSWORD,
            'db': self.REDIS_DB,
            'socket_timeout': self.REDIS_SOCKET_TIMEOUT,
            'socket_connect_timeout': self.REDIS_CONNECTION_TIMEOUT,
            'retry_on_timeout': self.REDIS_RETRY_ON_TIMEOUT,
            'max_connections': self.REDIS_MAX_CONNECTIONS
        }
        
        return params
    
    # AWS Settings
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-2")
    
    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Payment-related settings
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    PLATFORM_FEE_PERCENTAGE: Optional[int] = 3
    PAYOUT_THRESHOLD: float = 100.0
    MIN_PAYOUT_AMOUNT: float = 20.0
    
    ENVIRONMENT: str = "development"
    
    # Database URLs
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def REDIS_URL(self) -> str:
        if not self.REDIS_PASSWORD:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # class Config:
    #     case_sensitive = True
    #     env_file = ".env"
        
@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Database connection helpers
def get_db_connection_string() -> str:
    settings = get_settings()
    return settings.SQLALCHEMY_DATABASE_URL
