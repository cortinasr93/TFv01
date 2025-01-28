# tf-backend/api/auth/services.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from core.security import verify_password
from core.session import SessionManager
from core.models.publisher import Publisher
from core.models.aicompany import AICompany
from core.logging_config import get_logger, LogOperation

logger = get_logger(__name__)

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.session_manager = SessionManager()
        
    async def authenticate_user(self, email: str, password: str, user_type: str):
        """ 
        Authenticate a user and return their information
        """
        with LogOperation("authenticate_user", 
                        email=email,  # Email is needed for audit trail
                        user_type=user_type):
             
            try:
                # Get user based on type
                if user_type == 'publisher':
                    user = self.db.query(Publisher).filter(Publisher.email == email).first()
                    
                elif user_type == 'ai-company':
                    user = self.db.query(AICompany).filter(AICompany.email == email).first()

                else:
                    logger.warning("invalid_user_type", user_type=user_type)
                    raise HTTPException(status_code=400, detail="Invalid user type.")
                
                if not user:
                    logger.warning("user_not_found", 
                                 email=email, 
                                 user_type=user_type)
                    raise HTTPException(status_code=401, detail="Invalid email or password")
                
                # Verify password
                if not verify_password(password, user.hashed_password):
                    logger.warning("invalid_password", 
                                 email=email, 
                                 user_type=user_type)
                    raise HTTPException(status_code=401, detail="Invalid email or password")
                
                # Verify user.id exists
                if not hasattr(user, "id") or user.id is None:
                    logger.error("invalid_user_data", 
                               email=email,
                               user_type=user_type,
                               error="User ID missing")
                    raise HTTPException(status_code=500, detail="User data is invalid")
                
                user_data = {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.name,
                    "user_type": user_type,
                }
                
                # Create session
                logger.info("creating_session", 
                          user_id=str(user.id),
                          user_type=user_type)
                try:
                    session_id = self.session_manager.create_session(user_data)
                    logger.info("session_created", 
                              session_id=session_id,
                              user_id=str(user.id))
                except Exception as e:
                    logger.error("session_creation_failed",
                               user_id=str(user.id),
                               error=str(e),
                               exc_info=True)
                    raise
                
                logger.info("authentication_successful",
                          user_id=str(user.id),
                          user_type=user_type)
                
                return {
                    "session_id": session_id,
                    "user": user_data,
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error("authentication_error",
                           email=email,
                           user_type=user_type,
                           error=str(e),
                           exc_info=True)
                raise HTTPException(status_code=500, detail="Authentication failed")
    
    async def logout(self, session_id: str):
        """ 
        End user session
        """
        with LogOperation("logout", session_id=session_id):
            try: 
                # Get session data before ending it for logging
                session_data = self.session_manager.get_session(session_id)
                
                if self.session_manager.end_session(session_id):
                    if session_data:
                        logger.info("logout_successful",
                                    session_id=session_id,
                                    user_id=session_data.get("user_id"))
                    else:
                        logger.info("logout_successful",
                                    session_id=session_id,
                                    note="No session data found")
                    return {"message": "Logged out successfully"}
                
                logger.warning("invalid_session_logout",
                                session_id=session_id)
                raise HTTPException(status_code=400, detail="Invalid session")
            
            except HTTPException:
                raise
            except Exception as e:
                logger.error("logout_error",
                           session_id=session_id,
                           error=str(e),
                           exc_info=True)
                raise HTTPException(status_code=500, detail="Logout failed")