"""
Configuration settings for the Urban Green Spaces API.
Handles environment variables and default configurations for background tasks.
"""

import os
from typing import Dict, Any
from pathlib import Path


class Settings:
    """Application settings with environment variable support."""
    
    def __init__(self):
        # Database settings
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./urban_project.db")
        
        # Background task settings
        self.satellite_data_dir = os.getenv("SATELLITE_DATA_DIR", "/data/satellite")
        self.shapefile_dir = os.getenv("SHAPEFILE_DIR", "/data/shapefiles")
        self.temp_dir = os.getenv("TEMP_DIR", "/tmp")
        
        # Processing settings
        self.ndvi_threshold = float(os.getenv("NDVI_THRESHOLD", "0.3"))
        self.max_processing_time = int(os.getenv("MAX_PROCESSING_TIME", "3600"))  # 1 hour
        self.batch_size = int(os.getenv("BATCH_SIZE", "10"))  # Cities per batch
        
        # Schedule settings
        self.weekly_update_day = int(os.getenv("WEEKLY_UPDATE_DAY", "6"))  # Sunday = 6
        self.weekly_update_hour = int(os.getenv("WEEKLY_UPDATE_HOUR", "2"))  # 2 AM
        self.weekly_update_minute = int(os.getenv("WEEKLY_UPDATE_MINUTE", "0"))
        
        # Retry settings
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay = int(os.getenv("RETRY_DELAY", "300"))  # 5 minutes
        
        # Cache settings
        self.cache_ttl_hours = int(os.getenv("CACHE_TTL_HOURS", "168"))  # 1 week
        self.cache_cleanup_hour = int(os.getenv("CACHE_CLEANUP_HOUR", "3"))  # 3 AM
        
        # Logging settings
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "urban_api.log")
        self.log_max_size = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
        self.log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))
        
        # API settings
        self.cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        
        # JWT Authentication settings
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
        
        # Performance settings
        self.enable_background_tasks = os.getenv("ENABLE_BACKGROUND_TASKS", "true").lower() == "true"
        self.max_concurrent_updates = int(os.getenv("MAX_CONCURRENT_UPDATES", "3"))
        
        # External API settings
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.enable_external_data = os.getenv("ENABLE_EXTERNAL_DATA", "true").lower() == "true"
        self.external_api_timeout = int(os.getenv("EXTERNAL_API_TIMEOUT", "10"))
        self.external_api_cache_ttl = int(os.getenv("EXTERNAL_API_CACHE_TTL", "600"))  # 10 minutes
        
        # Data validation settings
        self.validate_satellite_data = os.getenv("VALIDATE_SATELLITE_DATA", "true").lower() == "true"
        self.min_coverage_percentage = float(os.getenv("MIN_COVERAGE_PERCENTAGE", "0.0"))
        self.max_coverage_percentage = float(os.getenv("MAX_COVERAGE_PERCENTAGE", "100.0"))
        
        # Create data directories if they don't exist
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.satellite_data_dir,
            self.shapefile_dir,
            self.temp_dir
        ]
        
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Warning: Could not create directory {directory}: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary for easy serialization."""
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_')
        }
    
    def get_cron_schedule(self) -> Dict[str, int]:
        """Get cron schedule settings for background tasks."""
        return {
            "day_of_week": self.weekly_update_day,
            "hour": self.weekly_update_hour,
            "minute": self.weekly_update_minute
        }
    
    def get_cache_settings(self) -> Dict[str, int]:
        """Get cache-related settings."""
        return {
            "ttl_hours": self.cache_ttl_hours,
            "cleanup_hour": self.cache_cleanup_hour
        }
    
    def get_processing_settings(self) -> Dict[str, Any]:
        """Get processing-related settings."""
        return {
            "ndvi_threshold": self.ndvi_threshold,
            "max_processing_time": self.max_processing_time,
            "batch_size": self.batch_size,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "validate_data": self.validate_satellite_data,
            "min_coverage": self.min_coverage_percentage,
            "max_coverage": self.max_coverage_percentage
        }


# Global settings instance
settings = Settings()


# Environment-specific configuration templates
DEVELOPMENT_CONFIG = """
# Development Environment Configuration
# Copy this to .env file in your backend directory

# Database
DATABASE_URL=sqlite:///./urban_project.db

# Data Directories (create these directories on your system)
SATELLITE_DATA_DIR=./data/satellite
SHAPEFILE_DIR=./data/shapefiles
TEMP_DIR=./data/temp

# Processing Settings
NDVI_THRESHOLD=0.3
BATCH_SIZE=5
MAX_PROCESSING_TIME=1800

# Schedule (for development, you might want to run more frequently)
WEEKLY_UPDATE_DAY=6
WEEKLY_UPDATE_HOUR=2
WEEKLY_UPDATE_MINUTE=0

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=urban_api_dev.log

# API Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000
API_HOST=127.0.0.1
API_PORT=8000

# JWT Authentication Settings
JWT_SECRET_KEY=your-secret-key-here-change-in-production-make-it-long-and-random
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Background Tasks
ENABLE_BACKGROUND_TASKS=true
MAX_CONCURRENT_UPDATES=2

# Validation
VALIDATE_SATELLITE_DATA=true
"""

PRODUCTION_CONFIG = """
# Production Environment Configuration
# Copy this to .env file in your production environment

# Database
DATABASE_URL=postgresql://user:password@localhost/urban_project

# Data Directories
SATELLITE_DATA_DIR=/var/data/urban-api/satellite
SHAPEFILE_DIR=/var/data/urban-api/shapefiles
TEMP_DIR=/tmp/urban-api

# Processing Settings
NDVI_THRESHOLD=0.3
BATCH_SIZE=10
MAX_PROCESSING_TIME=3600

# Schedule
WEEKLY_UPDATE_DAY=6
WEEKLY_UPDATE_HOUR=2
WEEKLY_UPDATE_MINUTE=0

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/urban-api/urban_api.log
LOG_MAX_SIZE=52428800
LOG_BACKUP_COUNT=10

# API Settings
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
API_HOST=0.0.0.0
API_PORT=8000

# JWT Authentication Settings
JWT_SECRET_KEY=super-secret-production-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Background Tasks
ENABLE_BACKGROUND_TASKS=true
MAX_CONCURRENT_UPDATES=3

# Performance
CACHE_TTL_HOURS=168

# Validation
VALIDATE_SATELLITE_DATA=true
MIN_COVERAGE_PERCENTAGE=0.0
MAX_COVERAGE_PERCENTAGE=100.0
"""


def save_config_template(config_type: str = "development", file_path: str = ".env.example"):
    """Save a configuration template to a file."""
    config_content = DEVELOPMENT_CONFIG if config_type == "development" else PRODUCTION_CONFIG
    
    try:
        with open(file_path, 'w') as f:
            f.write(config_content)
        print(f"Configuration template saved to {file_path}")
    except Exception as e:
        print(f"Error saving configuration template: {e}")


if __name__ == "__main__":
    # When run directly, create example configuration files
    save_config_template("development", ".env.development")
    save_config_template("production", ".env.production")
    print("Configuration templates created!")
    print("\nCurrent settings:")
    for key, value in settings.to_dict().items():
        print(f"  {key}: {value}")