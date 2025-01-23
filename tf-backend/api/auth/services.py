# tf-backend/api/auth/services.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from core.security import verify_password
from core.session import SessionManager
from core.models.publisher import Publisher
from core.models.aicompany import AICompany
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.session_manager = SessionManager()
        
    async def authenticate_user(self, email: str, password: str, user_type: str):
        """ 
        Authenticate a user and return their information
        """
        
        try:
            # Get user based on type
            if user_type == 'publisher':
                user = self.db.query(Publisher).filter(Publisher.email == email).first()
                
            elif user_type == 'ai-company':
                user = self.db.query(AICompany).filter(AICompany.email == email).first()

            else:
                raise HTTPException(status_code=400, detail="Invalid user type.")
            
            if not user:
                logger.warning(f"No user found for email: {email}")
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
            # Verify password
            if not verify_password(password, user.hashed_password):
                logger.warning(f"Failed login attempt for {email}")
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
            # Verify user.id exists
            if not hasattr(user, "id") or user.id is None:
                logger.error(f"User does not have a valid ID: {user}")
                raise HTTPException(status_code=500, detail="User data is invalid")
            
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "user_type": user_type,
            }
            
            logger.info(f"Creating session for user: {user_data['email']}")
            try:
                session_id = self.session_manager.create_session(user_data)
                logger.info(f"Session created successfully: {session_id}")
            except Exception as e:
                logger.error(f"Failed to create session: {str(e)}")
                raise
            
            return {
                "session_id": session_id,
                "user": user_data,
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(status_code=500, detail="Authentication failed")
    
    async def logout(self, session_id: str):
        """ 
        End user session
        """
        if self.session_manager.end_session(session_id):
            return {"message": "Logged out successfully"}
        raise HTTPException(status_code=400, detail="Invalid session")