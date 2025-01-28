import logging
import logging.handlers
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import structlog
from core.config import get_settings

settings = get_settings()

# Create logs directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

class CustomJSONFormatter(logging.Formatter):
    """Custom JSON formatter that includes additional context and timestamps"""
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields from record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def setup_logging() -> None:
    """Configure application-wide logging settings"""
    
    # Clear existing handlers
    logging.getLogger().handlers.clear()
    
    # Set up structured logging processor chain
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True
    )
    
    # Root logger config
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomJSONFormatter())
    root_logger.addHandler(console_handler)
    
    # File handlers for production
    if settings.ENVIRONMENT == "production":
        # Regular logs
        file_handler = logging.handlers.RotatingFileHandler(
            filename=LOG_DIR / "app.log",
            maxBytes=10 * 1024 * 1024, # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(CustomJSONFormatter())
        root_logger.addHandler(file_handler)
        
        # Error logs
        error_handler = logging.handlers.RotatingFileHandler(
            filename=LOG_DIR / "error.log",
            maxBytes=10 * 1024 * 1024, # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(CustomJSONFormatter())
        root_logger.addHandler(error_handler)
        
        # Access logs
        access_handler = logging.handlers.TimedRotatingFileHandler(
            filename=LOG_DIR / "access.log",
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        access_handler.setFormatter(CustomJSONFormatter())
        logging.getLogger("uvicorn.access").addHandler(access_handler)

# Custom logger factory for dependency injection
def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger with the given name

    Args:
        name (str): name: Name for the logger, typically __name__ of the module

    Returns:
        structlog.BoundLogger: A structured logger instance
    """
    return structlog.get_logger(name)

# Middleware for request logging
async def logging_middleware(request, call_next):
    """Middleware to log all incoming requests and their processing time"""
    logger = get_logger("request")
    start_time = datetime.now(timezone.utc)
    
    # Extract request details
    request_details = {
        "method": request.method,
        "path": str(request.url.path),
        "client_ip": request.client.host,
        "user_agent": request.headers.get("user-agent", ""),
    }
    
    try:
        # Process request and capture response
        response = await call_next(request)
        
        # Calculate processing time
        process_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Log successful request
        logger.info(
            "request_processed",
            status_code=response.status_code,
            duration=process_time,
            **request_details
        )
        
        return response
    
    except Exception as e:
        # Log failed request
        process_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.error(
            "request_failed",
            error=str(e),
            duration=process_time,
            **request_details,
            exc_info=True
        )
        raise

# Context manager for operation logging
class LogOperation:
    """Context Manager for logging operations with timing and outcome
    
    Example:
        with LogOperation("create_user", user_id=123):
            # Perform user creation
            create_user(...)
    """
    
    def __init__(self, operation_name: str, **kwargs):
        self.logger = get_logger("operation")
        self.operation_name = operation_name
        self.extra = kwargs
        self.start_time = None
        
    def __enter__(self):
        self.start_time = datetime.now(timezone.utc)
        self.logger.info(
            f"{self.operation_name}_started",
            **self.extra
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        
        if exc_type is None:
            # Operation succeeded
            self.logger.info(
                f"{self.operation_name}_completed",
                duration=duration,
                **self.extra
            )
        else:
            # Operation failed
            self.logger.error(
                f"{self.operation_name}_failed",
                error=str(exc_val),
                duration=duration,
                **self.extra,
                exc_info=True
            )
    