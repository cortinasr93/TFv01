# tf-backend/core/models/publisher.py

from sqlalchemy import Column, String, DateTime, Boolean, Float, UUID, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid
import enum
from core.database import Base

class PublisherOnboardingStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class Publisher(Base):
    __tablename__ = "publishers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    company_name = Column(String, nullable=False)
    website = Column(String)
    content_type = Column(String)
    message = Column(String)
    hashed_password = Column(String, nullable=False)
    
    #Stripe info
    stripe_account_id = Column(String, unique=True)
    payout_threshold = Column(Float, default=100.00)
    auto_payout = Column(Boolean, default=True)
    
    is_active = Column(Boolean, default=True)
    
    onboarding_status = Column(
        Enum(PublisherOnboardingStatus),
        nullable=False,
        default=PublisherOnboardingStatus.PENDING
    )
    settings = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    stripe_account = relationship("PublisherStripeAccount", back_populates="publisher", uselist=False)
    
    def __repr__(self):
        return f"<Publisher(name={self.company_name}, email={self.email})>"