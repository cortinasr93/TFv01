from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    model_config = ConfigDict(
        case_sensitive = True,
        env_file = ".env"
    )
    
    # Base URL
    BASE_URL: str = "http://localhost:3000"


    # PostgreSQL settings
    POSTGRES_USER: str = "trainfair_app"
    POSTGRES_PASSWORD: str = "password123"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "trainfair"
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "password123"
    REDIS_DB: int = 0
    
    # Payment-related settings
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    PLATFORM_FEE_PERCENTAGE: Optional[int] = 3
    PAYOUT_THRESHOLD: float = 100.0
    MIN_PAYOUT_AMOUNT: float = 20.0
    
    # Database URLs
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def REDIS_URL(self) -> str:
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

def get_redis_connection_params() -> dict:
    settings = get_settings()
    return {
        'host': settings.REDIS_HOST,
        'port': settings.REDIS_PORT,
        'password': settings.REDIS_PASSWORD,
        'db': settings.REDIS_DB
    }