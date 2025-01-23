# tf-backend/api/onboarding/services.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Dict, Optional, List
from datetime import datetime, timezone
from api.access_tokens.services import AccessTokenService
from core.models.payment import PublisherStripeAccount, AICompanyPaymentAccount
from core.security import hash_password
from core.models.publisher import Publisher, PublisherOnboardingStatus
from core.models.aicompany import AICompany, CompanyOnboardingStatus
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
        company_name: str,
        # password: str,
        website: str,
        content_type: str,
        message: str = None
    ) -> Dict:
        """ 
        Register a new publisher and initiate Stripe onboarding
        """
        try:
            # Check if publisher already exists
            existing_publisher = self.db.query(Publisher).filter_by(email=email).first()
            if existing_publisher:
                raise HTTPException(status_code=400, detail="Email already registered.")
            
            # hashed_password = hash_password(password)
            
            # Create publisher record
            publisher = Publisher(
                name=name,
                email=email,
                company_name=company_name,
                website=website,
                content_type=content_type,
                message=message,
                onboarding_status=PublisherOnboardingStatus.PENDING,
                #hashed_password=hashed_password,
                settings={
                    "registration_date": datetime.now(timezone.utc).isoformat(),
                    "initial_content_type": content_type,
                }
            )
            
            self.db.add(publisher)
            self.db.flush()
            
            logger.info(f"Successfully registered publisher: {company_name}")
            
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
                business_type="company",
                email=email,
                capabilities={
                    "transfers": {"requested": True},
                    "card_payments": {"requested": True}
                },
                business_profile={
                    "name": name,
                    "url": website,
                },
                metadata={
                    "publisher_id": str(publisher.id),
                    "content_type": content_type
                }
            )
            
            # Create account link for onboarding
            account_link = stripe.AccountLink.create(
                account=stripe_account.id,
                refresh_url=f"{settings.BASE_URL}/onboarding/refresh/{publisher.id}",
                return_url=f"{settings.BASE_URL}/dashboard/publisher/{publisher.id}",
                type="account_onboarding",
                collection_options={
                    "fields": "eventually_due"
                }
            )
            
            # Store Stripe account info
            publisher_stripe = PublisherStripeAccount(
                publisher_id=publisher.id,
                stripe_account_id=stripe_account.id,
                onboarding_complete=False,
                settings={
                    "account_link_created": datetime.now(timezone.utc).isoformat(),
                    "content_type": content_type
                }
            )
            self.db.add(publisher_stripe)
            self.db.commit()

            return {
                "publisher_id": str(publisher.id),
                "session_id": session_id,
                "onboarding_url": account_link.url,
                "stripe_account_id": stripe_account.id
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
        name: str,
        company_name: str,
        email: str,
        # password: str,
        website: str,
        use_cases: List[str],
        message: str = None,
    ) -> Dict:
        """
        Register a new AI company, set up Stripe customer, create access token
        """
        try:
            logger.info(f"Starting AI company registration for {company_name}")
            
            # Check for existing company
            existing_company = self.db.query(AICompany).filter_by(email=email).first()
            if existing_company:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Hash password
            # hashed_password = hash_password(password)

            # Create company record
            company = AICompany(
                name=name,
                company_name=company_name,
                email=email,
                website=website,
                use_cases=use_cases,
                message=message,
                onboarding_status=CompanyOnboardingStatus.PENDING,
                # hashed_password=hashed_password,
                metadata={
                    "registration_date": datetime.now(timezone.utc).isoformat(),
                    "initial_use_cases": use_cases
                }
            )
            
            self.db.add(company)
            self.db.flush()
            logger.info(f"Successfully registered AI company: {company_name}")
            
            try: 
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
                    billing_email=email
                )
                self.db.add(company_payment)
                self.db.flush()
                
                # Create access token
                token_service = AccessTokenService(self.db)
                token_result = await token_service.create_company_token(str(company.id))
                
                # Create session for new AI company
                session_id = self.session_manager.create_session({
                    "id": str(company.id),
                    "email": company.email,
                    "name": company.name,
                    "user_type": "ai-company"
                })
                
                self.db.commit()
                logger.info(f"Successfully completed registration for {company_name}")

                return {
                    "company_id": str(company.id),
                    "session_id": session_id,
                    "access_token": token_result.token,
                    "setup_complete": True
                }
            except Exception as inner_e:
            # If anything fails after company creation but before final commit,
            # rollback and log the specific error
                self.db.rollback()
                logger.error(f"Error during post-company creation setup: {str(inner_e)}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error during registration setup: {str(inner_e)}"
                )
        
        except stripe.error.StripeError as e:
            self.db.rollback()
            logger.error(f"Stripe error during company registration: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during company registration: {e}")
            raise HTTPException(status_code=500, detail="Error during registration")

    async def refresh_account_link(self, publisher_id: str) -> str:
        """ 
        Create new account link for publisher whose previous link expired
        """
        try:
            publisher_account = self.db.query(PublisherStripeAccount).filter_by(
                publisher_id=publisher_id
            ).first()
            
            if not publisher_account:
                raise HTTPException(status_code=404, detail="Publisher account not found")
            
            account_link = stripe.AccountLink.create(
                account=publisher_account.stripe_account_id,
                refresh_url=f"{settings.BASE_URL}/onboarding/refresh/{publisher_id}",
                return_url=f"{settings.BASE_URL}/onboarding/complete/{publisher_id}",
                type="account_onboarding",
                collect={"payments": True}
            )
            
            return account_link.url
        
        except stripe.error.StripeError as e:
            logger.error(f"Error refreshing account link: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
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
            
            publisher = self.db.query(Publisher).filter_by(id=publisher_id).first()
            
            if not publisher:
                raise HTTPException(status_code=404, detail="Publisher not found")

            # Verify Stripe account status
            stripe_account = stripe.Account.retrieve(publisher_account.stripe_account_id)
            
            publisher_account.onboarding_complete = stripe_account.details_submitted
            publisher_account.payout_enabled = stripe_account.payouts_enabled
            publisher_account.settings.update({
                "onboarding_completed_at": datetime.now(timezone.utc).isoformat() if stripe_account.details_submitted else None,
                "capabilities": stripe_account.capabilities,
                "requirements": stripe_account.requirements
            })
            self.db.commit()

            return {
                "onboarding_complete": publisher_account.onboarding_complete,
                "payout_enabled": publisher_account.payout_enabled,
                "email": publisher.email,
                "requirements": stripe_account.requirements,
                "next_steps": None if stripe_account.details_submitted else stripe_account.requirements.currently_due
            }
            
        except Exception as e:
            logger.error(f"Error completing publisher onboarding: {e}")
            raise HTTPException(status_code=500, detail="Error completing onboarding")   