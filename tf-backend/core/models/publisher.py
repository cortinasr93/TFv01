from sqlalchemy import Column, String, DateTime, Boolean, Float, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid
from core.database import Base

class Publisher(Base):
    __tablename__ = "publishers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    stripe_account_id = Column(String, unique=True)
    payout_threshold = Column(Float, default=100.00)
    auto_payout = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    settings = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    stripe_account = relationship("PublisherStripeAccount", back_populates="publisher", uselist=False)
    
    def __repr__(self):
        return f"<Publisher(name={self.name}, email={self.email})>"