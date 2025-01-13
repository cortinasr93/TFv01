import boto3
import logging
from botocore.exceptions import ClientError
from core.config import get_settings

logger = logging.getLogger(__name__)

async def send_email_to_info(
    name: str, 
    email: str, 
    company: str, 
    user_type: str, 
    message: str
):
    """ 
    Sends email to info@trainfair.io using Amazon SES
    """
    logger.info(f"Attempting to send email for {name}")
    settings = get_settings()
    
    subject = f"Contact Form Submission from {name}"
    body = (
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Company: {company}\n"
        f"User Type: {user_type}\n\n"
        f"Message:\n{message}"
    )
    
    # Configure Amazon SES client
    ses_client = boto3.client(
        "ses", 
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    
    sender_email = "rob@trainfair.io"
    recipient_email = "info@trainfair.io"
    
    try:
        logger.info("Attempting to send via SES...")
        response = ses_client.send_email(
            Source=sender_email,
            Destination={"ToAddresses": [recipient_email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}},
            },
        )
        logger.info(f"SES Response: {response}")
        return response
    except ClientError as e:
        error_message = e.response["Error"]["Message"]
        logger.error(f"AWS SES Error: {error_message}")
        raise Exception(f"Error sending email: {error_message}")