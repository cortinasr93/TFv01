from sqlalchemy import create_engine
from core.config import get_settings
from core.models.publisher import Base as PublisherBase
from core.models.aicompany import Base as AICompanyBase
from core.models.detection import Base as DetectionBase
from core.models.payment import Base as PaymentBase
from core.models.access_tokens import Base as TokenBase

def init_database():
    settings = get_settings()
    
    # Create engine with RDS connection
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
    
    try:
        # Create all tables
        PublisherBase.metadata.create_all(bind=engine)
        AICompanyBase.metadata.create_all(bind=engine)
        DetectionBase.metadata.create_all(bind=engine)
        PaymentBase.metadata.create_all(bind=engine)
        TokenBase.metadata.create_all(bind=engine)
        
        print("Successfully initialized database tables!")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_database()