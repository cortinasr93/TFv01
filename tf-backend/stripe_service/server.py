from core.models.payment import PublisherStripeAccount, AICompanyPaymentAccount, UsageRecord, PaymentTransaction
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from core.config import get_settings
from fastapi import HTTPException
import logging
import stripe

logger = logging.getLogger(__name__)
settings = get_settings()

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    def __init__(self, db: Session):
        self.db = db
    
    async def process_usage_payment(
        self,
        company_id: str,
        publisher_id: str,
        amount: float,
        usage_type: str
    ) -> Dict:
        """ 
        Process a payment for content usage
        """
        try:
            # Get company and publisher accounts
            company_account = self.db.query(AICompanyPaymentAccount).filter_by(
                company_id=company_id
            ).first()
            
            publisher_account = self.db.query(PublisherStripeAccount).filter_by(
                publisher_id=publisher_id
            ).first()
            
            if not company_account or not publisher_account:
                raise ValueError("Company or Publisher account not found")
            
            platform_fee = amount * (settings.PLATFORM_FEE_PERCENTAGE /100)
            publisher_amount = amount - platform_fee
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100), # Convert to cents
                currency="usd",
                customer=company_account.stripe_customer_id,
                transfer_data={
                    "destination": publisher_account.stripe_account_id,
                    "amount": int(publisher_amount * 100)
                },
                metadata={
                    "company_id": company_id,
                    "publisher_id": publisher_id,
                    "usage_type": usage_type
                }
            )
            
            # Record usage
            usage_record = UsageRecord(
                company_id=company_id,
                publisher_id=publisher_id,
                usage_type=usage_type,
                amount=amount,
                platform_fee=platform_fee,
                publisher_amount=publisher_amount,
                status="pending"
            )
            
            self.db.add(usage_record)
            
            # Record payment transaction
            payment_transaction = PaymentTransaction(
                company_id=company_id,
                stripe_payment_intent_id=payment_intent.id,
                amount=amount,
                status="pending"
            )
            
            self.db.add(payment_transaction)
            self.db.commit()
            
            return {
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error processing payment: {e}")
            raise
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            raise
    
    async def process_webhook(self, event_data: Dict) -> None:
        """ 
        Process Stripe webhook events
        """
        try:
            event_type = event_data["type"]
            
            if event_type == "account.updated":
                await self._handle_account_updated(event_data)
            elif event_type == "payment_intent.succeeded":
                await self._handle_payment_succeeded(event_data)
            elif event_type == "payout.failed":
                await self._handle_payout_failed(event_data)
        
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            raise
        
    async def _handle_account_updated(self, event_data: Dict) -> None:
        """ 
        Handle account.updated webhook event
        """
        account = event_data["account"]
        
        try:
            publisher_account = self.db.query(PublisherStripeAccount).filter_by(
                stripe_account_id=account["id"]
            ).first()
            
            if publisher_account:
                publisher_account.onboarding_complete = account["details_submitted"]
                publisher_account.payout_enabled = account["payouts_enabled"]
                self.db.commit()
        
        except Exception as e:
            logger.error(f"Error handling account update: {e}")
            raise
        
    async def _handle_payment_succeeded(self, event_data: Dict) -> None:
        """ 
        Handle payment_intent.succeeded webhook event
        """
        
        payment_intent = event_data["data"]["object"]
        
        try:
            # Update transaction status
            transaction = self.db.query(PaymentTransaction).filter_by(
                stripe_payment_intent_id=payment_intent["id"]
            ).first()
            
            if transaction:
                transaction.status="succeeded"
                
                # Udpate usage record
                usage_record = self.db.query(UsageRecord).filter_by(
                    company_id=transaction.company_id
                ).first()
                
                if usage_record:
                    usage_record.status = "processed"
                    usage_record.processed_at = datetime.now()
                
                self.db.commit()
        
        except Exception as e:
            logger.error(f"Error handling payment success: {e}")
            raise
    
    async def _handle_payout_failed(self, event_data: Dict) -> None:
        """ 
        Handle payout.failed webhook event
        """
        
        payout = event_data["data"]["object"]
        
        try:
            logger.error(f"Payout failed for account {payout['destination']}")
            # Implement retry logic or notification system
            
        except Exception as e:
            logger.error(f"Error handling payout failure: {e}")
            raise
    
        