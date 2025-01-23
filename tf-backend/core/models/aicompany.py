# tf-backend/core/models/aicompany.py

from sqlalchemy import Column, String, DateTime, UUID, ARRAY, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from core.database import Base
import enum

class CompanyOnboardingStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class AICompany(Base):
    __tablename__ = "ai_companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    company_name = Column(String, nullable=False)
    website = Column(String)
    use_cases = Column(ARRAY(String), nullable=False, default=[])
    message = Column(String)
    # hashed_password = Column(String, nullable=False)
    
    onboarding_status = Column(
        Enum(CompanyOnboardingStatus),
        nullable=False,
        default=CompanyOnboardingStatus.PENDING
    )
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    company_metadata = Column(JSON, default={})

    payment_account = relationship("AICompanyPaymentAccount", back_populates="company", uselist=False)
    access_tokens = relationship("AccessToken", back_populates="company")
    
    def __repr__(self):
        return f"<AICompany(company_name={self.company_name}, email={self.email})>"
 