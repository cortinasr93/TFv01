# tf-backend/core/models/access_tokens.py

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

class AccessToken(Base):
    """Stores API access tokens issued to AI companies"""
    __tablename__ = "access_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String, unique=True, nullable=False, index=True)
    
    # Ownership and relationships
    company_id = Column(UUID(as_uuid=True), ForeignKey('ai_companies.id'), nullable=False)
    
    # Token configuration
    status = Column(SQLEnum(AccessTokenStatus), nullable=False, default=AccessTokenStatus.ACTIVE)
    
    # Time validity
    created_at = Column(DateTime, default=datetime.now)
    revoked_at = Column(DateTime, nullable=True)
    
    # Usage tracking
    total_api_requests = Column(Integer, default=0)  # Number of API calls made
    total_ai_tokens_processed = Column(Integer, default=0)  # Total AI tokens processed
    
    # Additional configuration
    settings = Column(JSONB, default={})
    token_metadata = Column(JSONB, default={})

    # Relationships
    company = relationship("AICompany", back_populates="access_tokens")
    usage_records = relationship("APIUsageRecord", back_populates="access_token")
    
    def __repr__(self):
        return f"<AccessToken(id={self.id}, company={self.company_id}, status={self.status})>"

class APIUsageRecord(Base):
    """Records individual API usage events and AI token consumption"""
    __tablename__ = "api_usage_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    access_token_id = Column(UUID(as_uuid=True), ForeignKey('access_tokens.id'), nullable=False, index=True)
    publisher_id = Column(UUID(as_uuid=True), ForeignKey('publishers.id'), nullable=False, index=True)

    # Request details
    timestamp = Column(DateTime, default=datetime.now, index=True)
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
    usage_metadata = Column(JSONB, default={})

    # Relationship
    access_token = relationship("AccessToken", back_populates="usage_records")
    publisher = relationship("Publisher")

    def __repr__(self):
        return f"<APIUsageRecord(token_id={self.access_token_id}, ai_tokens={self.ai_tokens_processed})>"