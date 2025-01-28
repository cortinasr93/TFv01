# tf-backend/api/contact/services.py

import boto3
from core.logging_config import get_logger, LogOperation 
from botocore.exceptions import ClientError
from core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()

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
    with LogOperation("send_contact_email", sender_email=email, user_type=user_type):
        logger.info("initiating_contact_email", 
                   name=name,
                   company=company,
                   user_type=user_type)   
        
        try:
                   
            # Configure Amazon SES client
            ses_client = boto3.client(
                "ses", 
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
            
            subject = f"Contact Form Submission from {name}"
            body = (
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Company: {company}\n"
                f"User Type: {user_type}\n\n"
                f"Message:\n{message}"
            )
            
            sender_email = "rob@trainfair.io"
            recipient_email = "info@trainfair.io"
            
            logger.info("sending_ses_email",
                       recipient=recipient_email,
                       subject=subject)
            
            response = ses_client.send_email(
                Source=sender_email,
                Destination={"ToAddresses": [recipient_email]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": body}},
                },
            )
            logger.info("email_sent_successfully",
                       message_id=response['MessageId'],
                       sender=sender_email,
                       recipient=recipient_email)
            
            return response
            
        except ClientError as e:
            error_message = e.response["Error"]["Message"]
            logger.error("aws_ses_error",
                        error=error_message,
                        error_code=e.response["Error"]["Code"],
                        sender=sender_email,
                        recipient=recipient_email)
            raise Exception(f"Error sending email: {error_message}")
            
        except Exception as e:
            logger.error("email_send_failed",
                        error=str(e),
                        sender=sender_email,
                        recipient=recipient_email,
                        exc_info=True)
            raise