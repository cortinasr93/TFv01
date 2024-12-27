import os, sys

# Add project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from sqlalchemy.orm import Session
from core.database import SessionLocal
from core.models.publisher import Publisher
from core.models.detection import RequestLog
from datetime import datetime, timedelta
import json

def create_test_data():
    db = SessionLocal()
    try:
        # Create test publisher if doesn't exist
        test_publisher = db.query(Publisher).filter_by(name="Test Publisher").first()
        if not test_publisher:
            test_publisher = Publisher(
                name="Test Publisher",
                email="test@example.com",
            )
            db.add(test_publisher)
            db.commit()
            print("Created test publisher")
        
        # Create some sample request logs
        now = datetime.now()
        sample_logs = [
            RequestLog(
                ip_address="192.168.1.1",
                user_agent="Chrome",
                request_path="/test",
                request_method="GET",
                is_bot=False,
                publisher_id="test_publisher",
                timestamp=now - timedelta(hours=1)
            ),
            RequestLog(
                ip_address="192.168.1.2",
                user_agent="TestBot",
                request_path="/test",
                request_method="GET",
                is_bot=True,
                bot_name="TestBot",
                bot_type="Test",
                confidence_score=0.9,
                detection_methods=json.dumps(["pattern"]),
                publisher_id="test_publisher",
                timestamp=now - timedelta(minutes=30)
            ),
            RequestLog(
                ip_address="192.168.1.3",
                user_agent="GPTBot",
                request_path="/test",
                request_method="GET",
                is_bot=True,
                bot_name="OpenAI",
                bot_type="AI Training",
                confidence_score=1.0,
                detection_methods=json.dumps(["known_pattern"]),
                publisher_id="test_publisher",
                timestamp=now - timedelta(minutes=15)
            )
        ]
        
        for log in sample_logs:
            db.add(log)
        
        db.commit()
        print("Created sample request logs")
        
    except Exception as e:
        print(f"Error creating test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()