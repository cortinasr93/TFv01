# tf-backend/core/models/detection.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime
from core.database import Base

class RequestLog(Base):
    __tablename__ = "request_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    ip_address = Column(String, index=True, nullable=False)
    user_agent = Column(String, nullable=False)
    request_path = Column(String, nullable=False)
    request_method = Column(String, nullable=False)
    is_bot = Column(Boolean, nullable=False)
    is_ai_crawler = Column(Boolean, default=False)
    bot_name = Column(String)
    bot_type = Column(String)
    confidence_score = Column(Float)
    detection_methods = Column(String) #JSON string of detection methods
    publisher_id = Column(String, index=True)
    
    def __repr__(self):
        return f"<RequestLog(id={self.id}, ip={self.ip_address}, bot={self.is_bot})>"