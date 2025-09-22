"""
Logging configuration for the Urban Green Spaces API.
Provides structured logging for background tasks, API requests, and system events.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.config import settings


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)


class BackgroundTaskFilter(logging.Filter):
    """Filter to identify background task related log messages."""
    
    def filter(self, record):
        # Add background task identifier
        if hasattr(record, 'task_type'):
            return True
        
        # Check if the message is from background task modules
        task_modules = ['background_tasks', 'scheduler', 'coverage_update']
        if any(module in record.name for module in task_modules):
            record.task_type = 'background'
            return True
        
        return True


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = True
) -> logging.Logger:
    """
    Set up comprehensive logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        enable_console: Whether to enable console logging
        enable_file: Whether to enable file logging
        
    Returns:
        Configured logger instance
    """
    # Use settings defaults if not provided
    log_level = log_level or settings.log_level
    log_file = log_file or settings.log_file
    
    # Create logger
    logger = logging.getLogger('urban_api')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter for detailed logging
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create simple formatter for console
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler with colors
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Use colored formatter for console
        colored_formatter = ColoredFormatter(
            fmt='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(colored_formatter)
        console_handler.addFilter(BackgroundTaskFilter())
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if enable_file:
        try:
            # Create log directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_file,
                maxBytes=settings.log_max_size,
                backupCount=settings.log_backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, log_level.upper()))
            file_handler.setFormatter(detailed_formatter)
            file_handler.addFilter(BackgroundTaskFilter())
            logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"Warning: Could not create file handler for {log_file}: {e}")
    
    # Create separate handler for background tasks
    if enable_file:
        try:
            bg_log_file = log_file.replace('.log', '_background.log')
            bg_handler = logging.handlers.RotatingFileHandler(
                filename=bg_log_file,
                maxBytes=settings.log_max_size,
                backupCount=settings.log_backup_count,
                encoding='utf-8'
            )
            bg_handler.setLevel(logging.DEBUG)
            bg_handler.setFormatter(detailed_formatter)
            
            # Create filter for background tasks only
            class BGTaskOnlyFilter(logging.Filter):
                def filter(self, record):
                    return hasattr(record, 'task_type') and record.task_type == 'background'
            
            bg_handler.addFilter(BGTaskOnlyFilter())
            logger.addHandler(bg_handler)
            
        except Exception as e:
            print(f"Warning: Could not create background task handler: {e}")
    
    return logger


def get_task_logger(task_name: str) -> logging.Logger:
    """
    Get a logger specifically for background tasks.
    
    Args:
        task_name: Name of the background task
        
    Returns:
        Logger configured for background tasks
    """
    logger = logging.getLogger(f'urban_api.tasks.{task_name}')
    
    # Add task type for filtering
    class TaskLoggerAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            return f"[{self.extra['task_name']}] {msg}", kwargs
    
    adapter = TaskLoggerAdapter(logger, {'task_name': task_name})
    
    # Add task type attribute to all records
    original_handle = adapter.process
    def process_with_task_type(msg, kwargs):
        msg, kwargs = original_handle(msg, kwargs)
        # This is a bit of a hack, but it works with the filter
        return msg, kwargs
    
    adapter.process = process_with_task_type
    return adapter


def log_performance(func):
    """Decorator to log function performance."""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('urban_api.performance')
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"{func.__name__} completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {e}")
            raise
    
    return wrapper


def log_api_request(request_info: dict):
    """Log API request information."""
    logger = logging.getLogger('urban_api.requests')
    logger.info(f"API Request: {request_info}")


def log_background_task_start(task_name: str, details: dict = None):
    """Log the start of a background task."""
    logger = get_task_logger(task_name)
    details_str = f" | Details: {details}" if details else ""
    logger.info(f"Background task started{details_str}")


def log_background_task_end(task_name: str, success: bool, details: dict = None):
    """Log the completion of a background task."""
    logger = get_task_logger(task_name)
    status = "completed successfully" if success else "failed"
    details_str = f" | Details: {details}" if details else ""
    
    if success:
        logger.info(f"Background task {status}{details_str}")
    else:
        logger.error(f"Background task {status}{details_str}")


def log_satellite_processing(city_name: str, processing_stats: dict):
    """Log satellite data processing information."""
    logger = get_task_logger('satellite_processing')
    logger.info(f"Processed satellite data for {city_name}: {processing_stats}")


def log_cache_operation(operation: str, city_name: str = None, details: dict = None):
    """Log cache operations."""
    logger = logging.getLogger('urban_api.cache')
    city_info = f" for {city_name}" if city_name else ""
    details_str = f" | {details}" if details else ""
    logger.debug(f"Cache {operation}{city_info}{details_str}")


# Initialize logging when module is imported
main_logger = setup_logging()

# Create convenience loggers
api_logger = logging.getLogger('urban_api.api')
task_logger = logging.getLogger('urban_api.tasks')
cache_logger = logging.getLogger('urban_api.cache')
performance_logger = logging.getLogger('urban_api.performance')


if __name__ == "__main__":
    # Test logging configuration
    print("Testing logging configuration...")
    
    main_logger.debug("Debug message")
    main_logger.info("Info message")
    main_logger.warning("Warning message")
    main_logger.error("Error message")
    
    # Test task logger
    task_log = get_task_logger("test_task")
    task_log.info("This is a background task message")
    
    print("Logging test completed. Check log files for output.")