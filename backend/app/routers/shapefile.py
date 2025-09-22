from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import tempfile
import os
import json
from pathlib import Path

from app.database import get_db
from app.models import City, GreenCoverage
from app import schemas
from app.services.shapefile_service import shapefile_service
from app.services.cache_service import CacheService

# Create router
router = APIRouter(prefix="/shapefile", tags=["Shapefile & Satellite Imagery"])


@router.post("/info", response_model=schemas.ShapefileInfo)
async def get_shapefile_info(
    shapefile: UploadFile = File(..., description="Shapefile (.shp, .geojson, .gpkg)")
):
    """
    Get information about an uploaded shapefile.
    
    Returns:
        ShapefileInfo: Metadata about the shapefile including feature count, columns, and sample names
    """
    if not shapefile.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate file extension
    file_ext = Path(shapefile.filename).suffix.lower()
    if file_ext not in {'.shp', '.geojson', '.gpkg'}:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format: {file_ext}. Supported formats: .shp, .geojson, .gpkg"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        content = await shapefile.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Get shapefile information
        info = shapefile_service.get_shapefile_info(tmp_file_path)
        return schemas.ShapefileInfo(**info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing shapefile: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


@router.post("/validate-crs")
async def validate_coordinate_systems(
    shapefile: UploadFile = File(..., description="Shapefile for city boundaries"),
    raster: UploadFile = File(..., description="Satellite imagery raster file")
):
    """
    Validate that shapefile and raster have compatible coordinate systems.
    
    Returns:
        CoordinateSystemValidation: Validation results and recommendations
    """
    if not shapefile.filename or not raster.filename:
        raise HTTPException(status_code=400, detail="Both shapefile and raster files are required")
    
    # Validate file extensions
    shapefile_ext = Path(shapefile.filename).suffix.lower()
    raster_ext = Path(raster.filename).suffix.lower()
    
    if shapefile_ext not in {'.shp', '.geojson', '.gpkg'}:
        raise HTTPException(status_code=400, detail=f"Unsupported shapefile format: {shapefile_ext}")
    
    if raster_ext not in {'.tif', '.tiff', '.img', '.jp2'}:
        raise HTTPException(status_code=400, detail=f"Unsupported raster format: {raster_ext}")
    
    # Save files temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=shapefile_ext) as shp_tmp:
        shp_content = await shapefile.read()
        shp_tmp.write(shp_content)
        shp_tmp_path = shp_tmp.name
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=raster_ext) as raster_tmp:
        raster_content = await raster.read()
        raster_tmp.write(raster_content)
        raster_tmp_path = raster_tmp.name
    
    try:
        # Validate coordinate systems
        validation = shapefile_service.validate_coordinate_systems(shp_tmp_path, raster_tmp_path)
        return schemas.CoordinateSystemValidation(**validation)
    except Exception as e:
        return schemas.CoordinateSystemValidation(
            compatible=False,
            error=f"Error validating coordinate systems: {str(e)}"
        )
    finally:
        # Clean up temporary files
        for tmp_path in [shp_tmp_path, raster_tmp_path]:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


@router.post("/calculate-green-coverage", response_model=schemas.GreenCoverageCalculationResponse)
async def calculate_green_coverage_from_satellite(
    background_tasks: BackgroundTasks,
    shapefile: UploadFile = File(..., description="Shapefile containing city boundaries"),
    raster: UploadFile = File(..., description="Satellite imagery raster file"),
    request_data: str = Form(..., description="JSON string with calculation parameters"),
    save_to_database: bool = Form(False, description="Whether to save results to database"),
    db: Session = Depends(get_db)
):
    """
    Calculate green coverage percentage for a city using satellite imagery and shapefiles.
    
    Args:
        shapefile: Uploaded shapefile containing city boundaries
        raster: Uploaded satellite imagery raster file
        request_data: JSON string containing calculation parameters
        save_to_database: Whether to save the results to the database
        
    Returns:
        GreenCoverageCalculationResponse: Detailed green coverage analysis results
    """
    try:
        # Parse request data
        request_params = json.loads(request_data)
        calculation_request = schemas.GreenCoverageCalculationRequest(**request_params)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in request_data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request parameters: {str(e)}")
    
    if not shapefile.filename or not raster.filename:
        raise HTTPException(status_code=400, detail="Both shapefile and raster files are required")
    
    # Validate file extensions
    shapefile_ext = Path(shapefile.filename).suffix.lower()
    raster_ext = Path(raster.filename).suffix.lower()
    
    if shapefile_ext not in {'.shp', '.geojson', '.gpkg'}:
        raise HTTPException(status_code=400, detail=f"Unsupported shapefile format: {shapefile_ext}")
    
    if raster_ext not in {'.tif', '.tiff', '.img', '.jp2'}:
        raise HTTPException(status_code=400, detail=f"Unsupported raster format: {raster_ext}")
    
    # Save files temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=shapefile_ext) as shp_tmp:
        shp_content = await shapefile.read()
        shp_tmp.write(shp_content)
        shp_tmp_path = shp_tmp.name
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=raster_ext) as raster_tmp:
        raster_content = await raster.read()
        raster_tmp.write(raster_content)
        raster_tmp_path = raster_tmp.name
    
    try:
        # Initialize cache service
        cache_service = CacheService(db)
        
        # Use cache service to get or calculate green coverage
        def calculate_coverage():
            return shapefile_service.calculate_green_coverage_from_files(
                shapefile_path=shp_tmp_path,
                raster_path=raster_tmp_path,
                city_name=calculation_request.city_name,
                ndvi_threshold=calculation_request.ndvi_threshold,
                name_column=calculation_request.name_column,
                red_band_idx=calculation_request.red_band_idx,
                nir_band_idx=calculation_request.nir_band_idx
            )
        
        coverage_stats = cache_service.get_or_calculate_satellite_coverage(
            city_name=calculation_request.city_name,
            ndvi_threshold=calculation_request.ndvi_threshold,
            name_column=calculation_request.name_column,
            red_band_idx=calculation_request.red_band_idx,
            nir_band_idx=calculation_request.nir_band_idx,
            year=calculation_request.year,
            shapefile_path=shp_tmp_path,
            raster_path=raster_tmp_path,
            calculation_func=calculate_coverage
        )
        
        # Add year from request
        coverage_stats['year'] = calculation_request.year
        
        # Create response
        response = schemas.GreenCoverageCalculationResponse(**coverage_stats)
        
        # Save to database if requested
        if save_to_database:
            background_tasks.add_task(
                save_green_coverage_to_db,
                coverage_stats=coverage_stats,
                year=calculation_request.year,
                db_session=db
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating green coverage: {str(e)}")
    finally:
        # Clean up temporary files
        for tmp_path in [shp_tmp_path, raster_tmp_path]:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


def save_green_coverage_to_db(coverage_stats: dict, year: int, db_session: Session):
    """
    Background task to save green coverage results to database.
    
    Args:
        coverage_stats: Results from green coverage calculation
        year: Year of the satellite imagery
        db_session: Database session
    """
    try:
        # Find or create city
        city_name = coverage_stats['city_name']
        city = db_session.query(City).filter(City.name.ilike(city_name)).first()
        
        if not city:
            # Create new city if not found
            city = City(
                name=city_name,
                country="Unknown",  # Would need to be provided or derived
                area_km2=coverage_stats.get('total_area_km2')
            )
            db_session.add(city)
            db_session.commit()
            db_session.refresh(city)
        
        # Check if coverage data already exists for this city and year
        existing_coverage = db_session.query(GreenCoverage).filter(
            GreenCoverage.city_id == city.id,
            GreenCoverage.year == year
        ).first()
        
        if existing_coverage:
            # Update existing record
            for key, value in coverage_stats.items():
                if hasattr(existing_coverage, key) and key not in ['city_name', 'shapefile_path', 'raster_path']:
                    setattr(existing_coverage, key, value)
        else:
            # Create new record
            coverage_data = schemas.GreenCoverageEnhancedCreate(
                city_id=city.id,
                coverage_percentage=coverage_stats['green_coverage_percentage'],
                year=year,
                data_source=coverage_stats.get('data_source', 'Satellite Imagery Analysis'),
                measurement_method=coverage_stats.get('measurement_method', 'NDVI-based analysis'),
                total_area_km2=coverage_stats.get('total_area_km2'),
                green_area_km2=coverage_stats.get('green_area_km2'),
                ndvi_threshold=coverage_stats.get('ndvi_threshold'),
                mean_ndvi=coverage_stats.get('mean_ndvi'),
                std_ndvi=coverage_stats.get('std_ndvi'),
                min_ndvi=coverage_stats.get('min_ndvi'),
                max_ndvi=coverage_stats.get('max_ndvi'),
                coordinate_system=coverage_stats.get('coordinate_system'),
                total_pixels=coverage_stats.get('total_pixels'),
                green_pixels=coverage_stats.get('green_pixels'),
                processing_metadata=json.dumps({
                    'shapefile_source': 'uploaded',
                    'raster_source': 'uploaded',
                    'processing_timestamp': str(coverage_stats.get('timestamp'))
                })
            )
            
            # Set city_name for the model
            coverage_dict = coverage_data.dict()
            coverage_dict['city_name'] = city.name
            
            db_coverage = GreenCoverage(**coverage_dict)
            db_session.add(db_coverage)
        
        db_session.commit()
        
    except Exception as e:
        db_session.rollback()
        # Log error (would typically use proper logging)
        print(f"Error saving green coverage to database: {e}")


@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get information about supported file formats.
    
    Returns:
        Dictionary with supported shapefile and raster formats
    """
    return {
        "shapefile_formats": {
            ".shp": "ESRI Shapefile",
            ".geojson": "GeoJSON",
            ".gpkg": "GeoPackage"
        },
        "raster_formats": {
            ".tif": "GeoTIFF",
            ".tiff": "GeoTIFF",
            ".img": "ERDAS IMAGINE",
            ".jp2": "JPEG 2000"
        },
        "requirements": {
            "shapefile": "Must contain city/administrative boundaries",
            "raster": "Must be satellite imagery with Red and NIR bands for NDVI calculation",
            "coordinate_systems": "Shapefile and raster should ideally use the same CRS"
        },
        "recommendations": {
            "raster_resolution": "Higher resolution imagery (10m or better) provides more accurate results",
            "band_order": "Typical band order: Red=Band 1, NIR=Band 2 (adjust indices accordingly)",
            "ndvi_threshold": "0.3 is a common threshold for vegetation, but may need adjustment based on region"
        }
    }