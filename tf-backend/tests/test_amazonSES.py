import pytest
import boto3
from core.config import get_settings  # Use get_settings() to fetch settings

@pytest.mark.asyncio
async def test_send_real_email():
    """
    Sends an actual email via Amazon SES for testing purposes.
    """
    # Get settings
    settings = get_settings()

    # Initialize SES client with credentials from settings
    ses_client = boto3.client(
        "ses",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    
    # Email details
    sender_email = "info@trainfair.io"  # Must be a verified email in SES
    recipient_email = "info@trainfair.io"  # Replace with the test recipient
    subject = "Test Email from Amazon SES"
    body_text = "This is a test email sent using Amazon SES and Python."

    try:
        # Send the email
        response = ses_client.send_email(
            Source=sender_email,
            Destination={"ToAddresses": [recipient_email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body_text}},
            },
        )
        print(f"Email sent! Message ID: {response['MessageId']}")
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    except Exception as e:
        pytest.fail(f"Failed to send email: {str(e)}")
