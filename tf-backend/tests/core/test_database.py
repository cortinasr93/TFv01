import pytest
import psycopg2
import redis
from sqlalchemy.orm import Session
from datetime import datetime
from core.config import get_settings
from core.database import get_db
from core.models.detection import RequestLog

@pytest.fixture
def db_session():
    """Fixture to get a database session"""
    session = next(get_db())
    try:
        yield session
    finally:
        session.close()

def test_postgresql_connection():
    """Test basic PostgreSQL connection"""
    settings = get_settings()
    
    try:
        conn = psycopg2.connect(settings.SQLALCHEMY_DATABASE_URL)
        cursor = conn.cursor()
        
        # Test query execution
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL connection successful - Version: {version[0]}")
        
        cursor.close()
        conn.close()
        assert True
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        assert False

def test_redis_connection():
    """Test basic Redis connection and operations"""
    settings = get_settings()
    
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        # Test basic operations
        r.ping()
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        assert value == 'test_value'
        
        # Clean up
        r.delete('test_key')
        r.close()
        print("Redis connection and operations successful!")
        
    except Exception as e:
        print(f"Redis connection failed: {e}")
        assert False

def test_sqlalchemy_session(db_session: Session):
    """Test SQLAlchemy session and basic ORM operations"""
    try:
        # Ensure table exists
        from core.models.detection import Base, RequestLog
        from core.database import engine
        Base.metadata.create_all(bind=engine)
        
        # Create test request log
        test_log = RequestLog(
            ip_address="127.0.0.1",
            user_agent="test-agent",
            request_path="/test",
            request_method="GET",
            is_bot=True,
            bot_name="TestBot",
            bot_type="Test",
            confidence_score=1.0,
            detection_methods='["test"]',
            publisher_id="test_publisher"
        )
        
        # Test insert
        db_session.add(test_log)
        db_session.commit()
        
        # Get ID of the inserted record
        inserted_id = test_log.id
        print(f"Inserted record with ID: {inserted_id}")
        
        # Test query using ID for precise lookup
        queried_log = db_session.get(RequestLog, inserted_id)
        assert queried_log is not None, "Failed to retrieve inserted record"
        
        # Print actual values for debugging
        print(f"Retrieved record values:")
        print(f"bot_name: {queried_log.bot_name}")
        print(f"ip_address: {queried_log.ip_address}")
        print(f"is_bot: {queried_log.is_bot}")
        
        assert queried_log.bot_name == "TestBot", f"Expected 'TestBot', got '{queried_log.bot_name}'"
        assert queried_log.ip_address == "127.0.0.1"
        assert queried_log.is_bot == True
        
        # Test update
        queried_log.confidence_score = 0.9
        db_session.commit()
        
        # Verify update
        updated_log = db_session.get(RequestLog, inserted_id)
        assert updated_log.confidence_score == 0.9
        
        # Test delete
        db_session.delete(queried_log)
        db_session.commit()
        
        # Verify deletion
        deleted_log = db_session.get(RequestLog, inserted_id)
        assert deleted_log is None, "Record wasn't deleted"
        
        print("SQLAlchemy ORM operations successful!")
    
    except Exception as e:
        print(f"SQLAlchemy operations failed: {e}")
        print("Full error details:", e.__class__.__name__)
        import traceback
        print(traceback.format_exc())
        raise
    
def test_redis_request_logging():
    """Test Redis request logging functionality"""
    settings = get_settings()
    
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
        )
        
        # Test request logging
        publisher_id = "test_publisher"
        ip = "127.0.0.1"
        key = f"requests:{publisher_id}:{ip}"
        
        # Add test request
        test_request = {
            'timestamp': datetime.now().timestamp(),
            'path': '/test',
            'method': 'GET',
            'is_bot': True,
            'confidence': 0.9
        }
        
        r.lpush(key, str(test_request))
        r.expire(key, 3600)  # 1 hour expiry
        
        # Verify request was logged
        logged_requests = r.lrange(key, 0, -1)
        assert len(logged_requests) > 0
        
        # Clean up
        r.delete(key)
        r.close()
        
        print("Redis request logging test successful!")
        assert True
    except Exception as e:
        print(f"Redis request logging test failed: {e}")
        assert False

if __name__ == "__main__":
    pytest.main([__file__])