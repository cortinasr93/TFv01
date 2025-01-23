# tf-backend/api/auth/routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from pydantic import BaseModel
from .services import AuthService
from core.session import SessionManager

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str
    user_type: str # 'publisher' or 'ai-company'
    
@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """ 
    Authenticate a user
    """
    
    auth_service = AuthService(db)
    
    auth_result = await auth_service.authenticate_user(
        email=request.email,
        password=request.password,
        user_type=request.user_type
    )
    
    if not auth_result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create a session for authenticated user
    user_data = {
        "id": str(auth_result["user"]["id"]),
        "email": auth_result["user"]["email"],
        "user_type": auth_result["user"]["user_type"]
    }
    
    session_manager = SessionManager()
    session_id = session_manager.create_session(user_data)
    
    return {
        "session_id": session_id,
        "user_id": user_data["id"]
        }
    