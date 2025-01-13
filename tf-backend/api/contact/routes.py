from fastapi import APIRouter, HTTPException, Request
from .services import send_email_to_info
import logging

router = APIRouter(prefix="/api", tags=["contact"])
logger = logging.getLogger(__name__)

@router.post("/contact")
async def send_contact_email(request:Request):
    """ 
    Handles "Contact Us" form submission by calling email service
    """
    
    data = await request.json()
    logger.info(f"Received contat form submission: {data}")
    try:
        
        await send_email_to_info(
            name=data.get("name"),
            email=data.get("email"),
            company=data.get("company", "N/A"),
            user_type=data.get("userType", "Other"),
            message=data.get("message"),
        )
        logger.info("Email sent successfully")
        return {"message": "Email sent successfully"}
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))