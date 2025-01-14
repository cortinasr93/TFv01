from sqlalchemy import Column, String, DateTime, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from core.database import Base

class AICompany(Base):
    __tablename__ = "ai_companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    website = Column(String)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Add this relationship
    payment_account = relationship("AICompanyPaymentAccount", back_populates="company", uselist=False)
    access_tokens = relationship("AccessToken", back_populates="company")