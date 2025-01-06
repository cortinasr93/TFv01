from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Dict, Optional
from datetime import datetime
from core.models.payment import PublisherStripeAccount, AICompanyPaymentAccount
from core.security import hash_password
from core.models.publisher import Publisher
from core.models.aicompany import AICompany
from core.session import SessionManager
from core.config import get_settings
import stripe
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class OnboardingService:
    def __init__(self, db: Session):
        self.db = db
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.session_manager = SessionManager()
    
    async def register_publisher(
        self,
        name: str,
        email: str,
        password: str,
        website: str,
        content_type: str
    ) -> Dict:
        """ 
        Register a new publisher and initiate Stripe onboarding
        """
        try:
            # Check if publisher already exists
            existing_publisher = self.db.query(Publisher).filter_by(email=email).first()
            if existing_publisher:
                raise HTTPException(status_code=400, detail="Email already registered.")
            
            hashed_password = hash_password(password)
            
            # Create publisher record
            publisher = Publisher(
                name=name,
                email=email,
                website=website,
                content_type=content_type,
                hashed_password=hashed_password,
            )
            
            self.db.add(publisher)
            self.db.flush()
            
            # Create session for new publisher
            session_id = self.session_manager.create_session({
                "id": str(publisher.id),
                "email": publisher.email,
                "name": publisher.name,
                "user_type": "publisher"
            })
            
            stripe_account = stripe.Account.create(
                type="express",
                country="US",
                email=email,
                capabilities={
                    "transfers": {"requested": True},
                    "card_payments": {"requested": True}
                },
                business_type="company",
                business_profile={
                    "url": website
                }
            )
            
            # Create account link for onboarding
            account_link = stripe.AccountLink.create(
                account=stripe_account.id,
                refresh_url=f"{settings.BASE_URL}/onboarding/refresh",
                return_url=f"{settings.BASE_URL}/onboarding/complete",
                type="account_onboarding"
            )
            
            # Store Stripe account info
            publisher_stripe = PublisherStripeAccount(
                publisher_id=publisher.id,
                stripe_account_id=stripe_account.id,
                onboarding_complete=False
            )
            self.db.add(publisher_stripe)
            self.db.commit()

            return {
                "publisher_id": str(publisher.id),
                "session_id": session_id,
                "onboarding_url": account_link.url,
                "user_type": "publisher"
            }
        
        except stripe.error.StripeError as e:
            self.db.rollback()
            logger.error(f"Stripe error during publisher registration: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during publisher registration: {e}")
            raise HTTPException(status_code=500, detail="Error during registration")

    async def register_ai_company(
        self,
        company_name: str,
        email: str,
        password: str,
        website: str,
        billing_email: Optional[str] = None
    ) -> Dict:
        """
        Register a new AI company and set up Stripe customer
        """
        try:
            logger.info(f"Starting AI company registration for {company_name}")
            
            # Check for existing company
            existing_company = self.db.query(AICompany).filter_by(email=email).first()
            if existing_company:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Hash password
            hashed_password = hash_password(password)

            # Create company record
            company = AICompany(
                name=company_name,
                email=email,
                website=website,
                hashed_password=hashed_password
            )
            
            self.db.add(company)
            self.db.flush()
            logger.info(f"Created AI company record with ID: {company.id}")
            
            # Create stripe customer
            stripe_customer = stripe.Customer.create(
                email=email,
                name=company_name,
                metadata={
                    "company_id": str(company.id),
                    "website": website
                }
            )
            # Store payment account info
            company_payment = AICompanyPaymentAccount(
                company_id=company.id,
                stripe_customer_id=stripe_customer.id,
                billing_email=billing_email or email
            )
            self.db.add(company_payment)
            self.db.commit()
            logger.info(f"Successfully completed registration for {company_name}")

            return {
                "company_id": str(company.id),
                "setup_complete": True
            }
        
        except stripe.error.StripeError as e:
            self.db.rollback()
            logger.error(f"Stripe error during company registration: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during company registration: {e}")
            raise HTTPException(status_code=500, detail="Error during registration")

    async def complete_publisher_onboarding(self, publisher_id: str) -> Dict:
        """ 
        Complete publisher onboarding process
        """
        try:
            publisher_account = self.db.query(PublisherStripeAccount).filter_by(
                publisher_id=publisher_id
            ).first()

            if not publisher_account:
                raise HTTPException(status_code=404, detail="Publisher not found")

            # Verify Stripe account status
            stripe_account = stripe.Account.retrieve(publisher_account.stripe_account_id)
            
            publisher_account.onboarding_complete = stripe_account.details_submitted
            publisher_account.payout_enabled = stripe_account.payouts_enabled
            self.db.commit()

            return {
                "onboarding_complete": publisher_account.onboarding_complete,
                "payout_enabled": publisher_account.payout_enabled
            }
            
        except Exception as e:
            logger.error(f"Error completing publisher onboarding: {e}")
            raise HTTPException(status_code=500, detail="Error completing onboarding")   