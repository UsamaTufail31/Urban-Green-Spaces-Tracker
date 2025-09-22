# Background Tasks for Urban Green Spaces API

This document explains the background task system that provides automated weekly updates of green coverage data from satellite shapefiles.

## Overview

The background task system includes:
- **Weekly Green Coverage Updates**: Automatically processes satellite imagery to update green coverage data
- **Cache Management**: Cleans up expired cache entries to maintain performance
- **Flexible Scheduling**: Configurable timing and processing parameters
- **Comprehensive Logging**: Detailed logging for monitoring and debugging

## Features

### 1. Weekly Green Coverage Updates
- Automatically runs every Sunday at 2 AM (configurable)
- Processes satellite imagery and shapefiles for all cities
- Updates green coverage percentages using NDVI analysis
- Handles batch processing to avoid system overload
- Includes retry logic for failed processing

### 2. Cache Management
- Daily cleanup of expired cache entries
- Intelligent cache invalidation after updates
- Configurable cache TTL (Time To Live)

### 3. Manual Triggers
- API endpoints to manually trigger updates
- Support for city-specific or global updates
- Real-time status monitoring

## Configuration

All settings can be configured via environment variables. Copy `.env.example` to `.env` and modify as needed.

### Key Settings

```bash
# Enable/disable background tasks
ENABLE_BACKGROUND_TASKS=true

# Schedule (Sunday at 2 AM)
WEEKLY_UPDATE_DAY=6  # 0=Monday, 6=Sunday
WEEKLY_UPDATE_HOUR=2
WEEKLY_UPDATE_MINUTE=0

# Processing settings
NDVI_THRESHOLD=0.3
BATCH_SIZE=10
MAX_PROCESSING_TIME=3600  # 1 hour max

# Data directories
SATELLITE_DATA_DIR=/data/satellite
SHAPEFILE_DIR=/data/shapefiles

# Logging
LOG_LEVEL=INFO
LOG_FILE=urban_api.log
```

## Data Requirements

### Directory Structure
```
/data/
├── satellite/          # Satellite imagery files (.tif, .tiff)
│   ├── city_name.tif
│   ├── region_2024.tif
│   └── ...
├── shapefiles/         # City boundary shapefiles
│   ├── cities.shp
│   ├── municipalities.geojson
│   └── ...
└── temp/              # Temporary processing files
```

### Supported Formats
- **Raster**: .tif, .tiff, .img, .jp2
- **Vector**: .shp, .geojson, .gpkg

### File Naming Conventions
For city-specific processing, files should include the city name:
- `new_york_2024.tif`
- `london_boundaries.shp`
- `paris_satellite_data.tiff`

## API Endpoints

### Background Task Management

```bash
# Get task status
GET /background-tasks/status

# Start background tasks
POST /background-tasks/start

# Stop background tasks
POST /background-tasks/stop

# Trigger manual update (all cities)
POST /background-tasks/trigger-update

# Trigger manual update (specific city)
POST /background-tasks/trigger-update?city_name=New%20York
```

### Example Response
```json
{
  "status": "running",
  "jobs": [
    {
      "id": "weekly_green_coverage_update",
      "name": "Weekly Green Coverage Update",
      "next_run": "2024-01-07T02:00:00",
      "trigger": "cron[day_of_week='6', hour='2', minute='0']"
    }
  ],
  "config": {
    "ndvi_threshold": 0.3,
    "batch_size": 10,
    "max_processing_time": 3600
  },
  "settings": {
    "enabled": true,
    "schedule": {
      "day_of_week": 6,
      "hour": 2,
      "minute": 0
    }
  }
}
```

## Installation & Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Create Configuration
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Create Data Directories
```bash
mkdir -p data/satellite data/shapefiles data/temp
```

### 4. Initialize Database
```bash
python -m app.init_db
```

### 5. Start the API
```bash
python app/main.py
```

## Monitoring & Logging

### Log Files
- `urban_api.log`: Main application log
- `urban_api_background.log`: Background task specific logs

### Log Levels
- **DEBUG**: Detailed processing information
- **INFO**: General status updates
- **WARNING**: Non-critical issues
- **ERROR**: Processing failures

### Example Log Output
```
2024-01-07 02:00:00 | INFO     | [weekly_green_coverage_update] Background task started
2024-01-07 02:00:01 | INFO     | [process_city_new_york] Processing green coverage for New York
2024-01-07 02:00:15 | INFO     | [process_city_new_york] Updated green coverage for New York: 34.5%
2024-01-07 02:05:30 | INFO     | [weekly_green_coverage_update] Background task completed successfully
```

## Troubleshooting

### Common Issues

1. **No Cities Processing**
   - Check if satellite data exists in configured directories
   - Verify file naming conventions
   - Check logs for data availability messages

2. **Processing Failures**
   - Verify NDVI threshold is appropriate (0.1-0.5)
   - Check satellite data quality and format
   - Ensure coordinate systems match between raster and vector data

3. **Background Tasks Not Running**
   - Verify `ENABLE_BACKGROUND_TASKS=true`
   - Check scheduler status via API
   - Review startup logs for errors

### Performance Optimization

1. **Batch Size**: Reduce if system is overloaded
2. **Processing Time**: Increase for complex datasets
3. **Cache TTL**: Adjust based on update frequency needs
4. **Log Level**: Use INFO or WARNING in production

## Development

### Testing Background Tasks
```bash
# Test configuration
python app/config.py

# Test logging
python app/logging_config.py

# Manual update trigger
curl -X POST http://localhost:8000/background-tasks/trigger-update?city_name=TestCity
```

### Adding New Tasks
1. Add task function to `BackgroundTaskService`
2. Register in `start_scheduler()` method
3. Add appropriate logging and error handling
4. Update configuration as needed

## Production Deployment

### Considerations
- Use PostgreSQL instead of SQLite for better concurrency
- Set up log rotation and monitoring
- Configure appropriate batch sizes for server capacity
- Use dedicated storage for satellite data
- Set up backup procedures for processed data

### Example Production Config
```bash
# Production optimized settings
ENABLE_BACKGROUND_TASKS=true
BATCH_SIZE=20
MAX_PROCESSING_TIME=7200
LOG_LEVEL=INFO
CACHE_TTL_HOURS=336  # 2 weeks
DATABASE_URL=postgresql://user:pass@localhost/urban_db
```