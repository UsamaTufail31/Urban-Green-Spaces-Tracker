# Satellite Imagery & Shapefile Integration

This document describes the new satellite imagery and shapefile integration capabilities added to the Urban Green Spaces API.

## Overview

The enhanced API now supports:
- ✅ Uploading and processing shapefiles containing city boundaries
- ✅ Processing satellite imagery (GeoTIFF, JPEG2000, etc.)
- ✅ Calculating green coverage using NDVI (Normalized Difference Vegetation Index)
- ✅ Storing detailed satellite imagery analysis results
- ✅ Validating coordinate systems between shapefiles and rasters

## New API Endpoints

### 1. Get Shapefile Information
**Endpoint:** `POST /shapefile/info`
- Upload a shapefile to get metadata information
- Supported formats: `.shp`, `.geojson`, `.gpkg`
- Returns feature count, columns, coordinate system, and sample city names

### 2. Validate Coordinate Systems
**Endpoint:** `POST /shapefile/validate-crs`
- Upload both shapefile and raster to check CRS compatibility
- Helps ensure accurate spatial analysis
- Provides recommendations for coordinate system alignment

### 3. Calculate Green Coverage from Satellite Imagery
**Endpoint:** `POST /shapefile/calculate-green-coverage`
- Main endpoint for green coverage analysis
- Requires shapefile (city boundaries) and satellite imagery
- Calculates NDVI and determines vegetation coverage percentage
- Optionally saves results to database

### 4. Get Supported Formats
**Endpoint:** `GET /shapefile/supported-formats`
- Returns information about supported file formats
- Includes requirements and recommendations

## How It Works

### 1. NDVI Calculation
The service calculates NDVI using the formula:
```
NDVI = (NIR - Red) / (NIR + Red)
```

Where:
- NIR = Near-infrared band
- Red = Red band

### 2. Vegetation Classification
- NDVI values range from -1 to +1
- Default threshold: 0.3 (configurable)
- Values ≥ threshold are classified as vegetation
- Green coverage % = (Green pixels / Total pixels) × 100

### 3. Spatial Analysis
- City polygon extracted from shapefile
- Raster data clipped to city boundary
- Only pixels within city boundary are analyzed
- Results include area calculations in m² and km²

## Request Format

### Calculate Green Coverage Request
```json
{
  "city_name": "New York",
  "ndvi_threshold": 0.3,
  "name_column": "NAME",
  "red_band_idx": 0,
  "nir_band_idx": 1,
  "year": 2023
}
```

### Parameters:
- `city_name`: Name of city in the shapefile
- `ndvi_threshold`: Vegetation threshold (0.0-1.0, default: 0.3)
- `name_column`: Column containing city names (default: "NAME")
- `red_band_idx`: Red band index in raster (0-based, default: 0)
- `nir_band_idx`: NIR band index in raster (0-based, default: 1)
- `year`: Year of satellite imagery

## Response Format

### Green Coverage Calculation Response
```json
{
  "city_name": "New York",
  "green_coverage_percentage": 45.67,
  "total_pixels": 1234567,
  "green_pixels": 563456,
  "total_area_m2": 789012345.0,
  "green_area_m2": 360234567.0,
  "total_area_km2": 789.01,
  "green_area_km2": 360.23,
  "ndvi_threshold": 0.3,
  "mean_ndvi": 0.25,
  "std_ndvi": 0.35,
  "min_ndvi": -0.8,
  "max_ndvi": 0.9,
  "data_source": "Satellite Imagery Analysis",
  "measurement_method": "NDVI-based analysis (threshold: 0.3)",
  "coordinate_system": "EPSG:4326",
  "year": 2023
}
```

## Database Schema Updates

The `green_coverage` table has been enhanced with new fields:

### Satellite Imagery Fields:
- `total_area_km2`: Total city area in km²
- `green_area_km2`: Green area in km²
- `ndvi_threshold`: NDVI threshold used
- `mean_ndvi`, `std_ndvi`, `min_ndvi`, `max_ndvi`: NDVI statistics
- `coordinate_system`: Spatial reference system
- `total_pixels`, `green_pixels`: Pixel counts
- `processing_metadata`: JSON metadata
- `created_at`, `updated_at`: Timestamps

## File Format Support

### Shapefiles:
- ✅ ESRI Shapefile (`.shp`)
- ✅ GeoJSON (`.geojson`)
- ✅ GeoPackage (`.gpkg`)

### Satellite Imagery:
- ✅ GeoTIFF (`.tif`, `.tiff`)
- ✅ ERDAS IMAGINE (`.img`)
- ✅ JPEG 2000 (`.jp2`)

## Requirements

### Shapefile Requirements:
- Must contain polygon geometries representing city/administrative boundaries
- Should have a column with city names (typically "NAME", "CITY", etc.)
- Coordinate system should match raster data for best results

### Satellite Imagery Requirements:
- Must contain at least Red and Near-infrared bands
- Bands should be in the correct order or indices specified
- Should cover the area of interest defined in the shapefile
- Resolution: Higher resolution (≤30m) recommended for urban areas

## Installation

### 1. Install Dependencies
```bash
pip install geopandas rasterio shapely numpy pandas
```

### 2. Run Database Migration
```bash
python migrate_database.py
```

### 3. Start Server
```bash
python -m uvicorn app.main:app --reload
```

## Usage Examples

### 1. Using cURL
```bash
# Get shapefile information
curl -X POST "http://localhost:8000/shapefile/info" \
  -H "Content-Type: multipart/form-data" \
  -F "shapefile=@cities.shp"

# Calculate green coverage
curl -X POST "http://localhost:8000/shapefile/calculate-green-coverage" \
  -H "Content-Type: multipart/form-data" \
  -F "shapefile=@cities.shp" \
  -F "raster=@satellite_image.tif" \
  -F "request_data={\"city_name\":\"New York\",\"year\":2023}" \
  -F "save_to_database=true"
```

### 2. Using Python requests
```python
import requests

# Calculate green coverage
files = {
    'shapefile': open('cities.shp', 'rb'),
    'raster': open('satellite_image.tif', 'rb')
}

data = {
    'request_data': json.dumps({
        'city_name': 'New York',
        'ndvi_threshold': 0.3,
        'year': 2023
    }),
    'save_to_database': True
}

response = requests.post(
    'http://localhost:8000/shapefile/calculate-green-coverage',
    files=files,
    data=data
)

result = response.json()
print(f"Green coverage: {result['green_coverage_percentage']:.2f}%")
```

## Best Practices

### 1. Data Preparation
- Ensure shapefiles and rasters use the same coordinate system
- Use high-quality satellite imagery (Landsat, Sentinel-2, etc.)
- Verify band ordering (Red, NIR) before processing

### 2. NDVI Threshold Selection
- Urban areas: 0.2-0.3
- Rural areas: 0.3-0.4
- Arid regions: 0.1-0.2
- Adjust based on local vegetation characteristics

### 3. Performance Optimization
- Use compressed GeoTIFF format for rasters
- Consider tiling large rasters
- Limit analysis to areas of interest using clipped shapefiles

## Troubleshooting

### Common Issues:

1. **"No valid pixels found"**
   - Check coordinate system compatibility
   - Verify polygon intersects with raster bounds
   - Ensure raster contains valid data

2. **"City not found"**
   - Check city name spelling and case
   - Verify name column parameter
   - Use `/shapefile/info` to see available cities

3. **"Unsupported file format"**
   - Check file extensions
   - Use `/shapefile/supported-formats` for valid formats

4. **Poor NDVI results**
   - Verify Red and NIR band indices
   - Check band ordering in satellite imagery
   - Adjust NDVI threshold for local conditions

## Testing

Run the test suite to verify installation:
```bash
python test_shapefile_integration.py
```

The test suite includes:
- ✅ Shapefile loading and processing
- ✅ Raster data handling
- ✅ NDVI calculation
- ✅ Green coverage analysis
- ✅ Error handling
- ✅ Performance testing

## API Documentation

Visit `http://localhost:8000/docs` when the server is running to see the interactive API documentation with detailed parameter descriptions and example requests.

## Future Enhancements

Potential improvements for future versions:
- Support for additional vegetation indices (EVI, SAVI, etc.)
- Time series analysis for multiple years
- Land cover classification beyond vegetation
- Integration with cloud-based satellite imagery services
- Automated coordinate system reprojection
- Batch processing for multiple cities

---

For technical support or questions, please refer to the main project documentation or create an issue in the project repository.