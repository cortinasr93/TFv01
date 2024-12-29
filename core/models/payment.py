from sqlalchemy import Column, String, Boolean, Float, DateTime, ForeignKey, UUID, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from core.database import Base

class PublisherStripeAccount(Base):
    """Stores Stripe Connect account information for publishers"""
    __tablename__ = "publisher_stripe_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    publisher_id = Column(UUID(as_uuid=True), ForeignKey('publishers.id'), nullable=False)
    stripe_account_id = Column(String, unique=True, nullable=False)
    onboarding_complete = Column(Boolean, default=False)
    payout_enabled = Column(Boolean, default=False)
    current_balance = Column(Float, default=0.0)
    last_payout_at = Column(DateTime, nullable=True)
    payout_schedule = Column(String, default='weekly')  # weekly, monthly, threshold
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    publisher = relationship("Publisher", back_populates="stripe_account")
    usage_records = relationship("UsageRecord", back_populates="publisher_account")
    
    def __repr__(self):
        return f"<PublisherStripeAccount(publisher_id={self.publisher_id}, balance=${self.current_balance:.2f})>"

class AICompanyPaymentAccount(Base):
    """Stores Stripe customer information for AI companies"""
    __tablename__ = "ai_company_payment_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('ai_companies.id'), nullable=False)
    stripe_customer_id = Column(String, unique=True, nullable=False)
    default_payment_method = Column(String, nullable=True)
    billing_email = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("AICompany", back_populates="payment_account")
    usage_records = relationship("UsageRecord", back_populates="company_account")
    payment_transactions = relationship("PaymentTransaction", back_populates="company_account")

    def __repr__(self):
        return f"<AICompanyPaymentAccount(company_id={self.company_id}, customer_id={self.stripe_customer_id})>"

class UsageRecord(Base):
    """Tracks usage and billing records"""
    __tablename__ = "usage_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('ai_company_payment_accounts.id'), nullable=False)
    publisher_id = Column(UUID(as_uuid=True), ForeignKey('publisher_stripe_accounts.id'), nullable=False)
    usage_type = Column(String, nullable=False)  # 'training', 'rag', etc.
    amount = Column(Float, nullable=False)
    platform_fee = Column(Float, nullable=False)
    publisher_amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)  # 'pending', 'processed', 'failed'
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company_account = relationship("AICompanyPaymentAccount", back_populates="usage_records")
    publisher_account = relationship("PublisherStripeAccount", back_populates="usage_records")

    def __repr__(self):
        return f"<UsageRecord(company_id={self.company_id}, amount=${self.amount:.2f}, status={self.status})>"

class PaymentTransaction(Base):
    """Records all payment transactions"""
    __tablename__ = "payment_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('ai_company_payment_accounts.id'), nullable=False)
    stripe_payment_intent_id = Column(String, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)  # 'pending', 'succeeded', 'failed'
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    company_account = relationship("AICompanyPaymentAccount", back_populates="payment_transactions")

    def __repr__(self):
        return f"<PaymentTransaction(payment_intent={self.stripe_payment_intent_id}, amount=${self.amount:.2f})>"