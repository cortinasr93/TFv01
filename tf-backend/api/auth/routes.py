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
    
    
    return {
        "session_id": auth_result["session_id"],
        "user_id": auth_result["user"]["id"]
        }
    