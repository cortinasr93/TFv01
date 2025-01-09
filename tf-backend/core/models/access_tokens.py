from sqlalchemy import Column, String, DateTime, Boolean, Float, ForeignKey, UUID, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import enum
import uuid
from core.database import Base

class AccessTokenStatus(enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
    SUSPENDED = "suspended"

class AccessType(enum.Enum):
    TRAINING = "training"  # For model training access
    RAG = "rag"           # For retrieval-augmented generation
    BOTH = "both"         # Access for both purposes

class AccessToken(Base):
    """Stores API access tokens issued to AI companies"""
    __tablename__ = "access_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String, unique=True, nullable=False, index=True)
    
    # Ownership and relationships
    company_id = Column(UUID(as_uuid=True), ForeignKey('ai_companies.id'), nullable=False)
    publisher_id = Column(UUID(as_uuid=True), ForeignKey('publishers.id'), nullable=False)
    
    # Token configuration
    access_type = Column(SQLEnum(AccessType), nullable=False)
    status = Column(SQLEnum(AccessTokenStatus), nullable=False, default=AccessTokenStatus.ACTIVE)
    
    # Rate limits and quotas
    daily_request_limit = Column(Integer, nullable=True)
    monthly_ai_token_limit = Column(Integer, nullable=True)  # Limit on AI tokens processed
    rate_limit_per_minute = Column(Integer, default=60)
    
    # Time validity
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    
    # Usage tracking
    total_api_requests = Column(Integer, default=0)  # Number of API calls made
    total_ai_tokens_processed = Column(Integer, default=0)  # Total AI tokens processed
    
    # Additional configuration
    settings = Column(JSONB, default={})
    metadata = Column(JSONB, default={})

    # Relationships
    company = relationship("AICompany", back_populates="access_tokens")
    publisher = relationship("Publisher", back_populates="access_tokens")
    usage_records = relationship("APIUsageRecord", back_populates="access_token")

    def __repr__(self):
        return f"<AccessToken(id={self.id}, company={self.company_id}, status={self.status})>"

class APIUsageRecord(Base):
    """Records individual API usage events and AI token consumption"""
    __tablename__ = "api_usage_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    access_token_id = Column(UUID(as_uuid=True), ForeignKey('access_tokens.id'), nullable=False)
    
    # Request details
    timestamp = Column(DateTime, default=datetime.utcnow)
    request_path = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # AI token usage
    ai_tokens_processed = Column(Integer, default=0)  # Number of AI tokens processed in this request
    content_size_bytes = Column(Integer, nullable=True)  # Size of content accessed
    content_type = Column(String, nullable=True)  # Type of content (text, code, etc.)
    
    # Success/failure tracking
    is_success = Column(Boolean, default=True)
    error_message = Column(String, nullable=True)
    
    # Additional data
    metadata = Column(JSONB, default={})

    # Relationship
    access_token = relationship("AccessToken", back_populates="usage_records")

    def __repr__(self):
        return f"<APIUsageRecord(token_id={self.access_token_id}, ai_tokens={self.ai_tokens_processed})>"