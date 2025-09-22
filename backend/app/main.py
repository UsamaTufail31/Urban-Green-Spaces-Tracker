from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import math
import asyncio

from app.database import get_db
from app.models import City, Park, GreenCoverage, Feedback
from app import schemas
from app.routers import shapefile, auth
from app.auth_dependencies import get_admin_user, get_current_user_optional
from app.services.cache_service import CacheService
from app.services.background_tasks import background_task_service
from app.services.external_data_service import get_external_data_service, cleanup_external_data_service
from app.config import settings
from app.logging_config import setup_logging, api_logger

# Initialize logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="Urban Green Spaces API",
    description="API for managing urban green spaces, parks, and green coverage data with satellite imagery integration and automated weekly updates",
    version="1.1.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(shapefile.router)


# Background task lifecycle events
@app.on_event("startup")
async def startup_event():
    """Start background tasks when the application starts."""
    api_logger.info("Starting Urban Green Spaces API")
    api_logger.info(f"Configuration: {settings.to_dict()}")
    
    if settings.enable_background_tasks:
        await background_task_service.start_scheduler()
        api_logger.info("Background task scheduler started")
    else:
        api_logger.info("Background tasks disabled in configuration")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks when the application shuts down."""
    api_logger.info("Shutting down Urban Green Spaces API")
    await background_task_service.stop_scheduler()
    await cleanup_external_data_service()
    api_logger.info("External data service cleanup completed")


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) using the Haversine formula.
    
    Returns distance in kilometers.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r


@app.get("/")
async def root(current_user: Optional[schemas.User] = Depends(get_current_user_optional)):
    """Root endpoint providing API information."""
    endpoints = {
        "cities": "/cities",
        "parks": "/parks",
        "green_coverage": "/green-coverage",
        "coverage_compare": "/coverage/compare",
        "feedback": "/feedback",
        "background_tasks": "/background-tasks/status",
        "manual_update": "/background-tasks/trigger-update",
        "auth": "/auth",
        "docs": "/docs"
    }
    
    response = {
        "message": "Urban Green Spaces API",
        "version": "1.1.0",
        "features": [
            "Satellite imagery processing",
            "Weekly automated green coverage updates",
            "Real-time park search",
            "Cache management",
            "Background task monitoring",
            "JWT Authentication for admin dashboard"
        ],
        "endpoints": endpoints
    }
    
    if current_user:
        response["authenticated_user"] = {
            "username": current_user.username,
            "role": current_user.role,
            "full_name": current_user.full_name
        }
        
        if current_user.role == "admin":
            response["admin_endpoints"] = {
                "create_city": "POST /cities",
                "update_city": "PUT /cities/{id}",
                "delete_city": "DELETE /cities/{id}",
                "create_park": "POST /parks",
                "update_park": "PUT /parks/{id}",
                "delete_park": "DELETE /parks/{id}",
                "create_green_coverage": "POST /green-coverage",
                "manage_users": "/auth/users",
                "cache_management": "/cache",
                "background_tasks": "/background-tasks"
            }
    else:
        response["authentication"] = {
            "login": "POST /auth/login",
            "register": "POST /auth/register (admin only)",
            "token_info": "GET /auth/me"
        }
    
    return response


@app.post("/feedback", response_model=schemas.FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    """
    Submit user feedback.
    
    Args:
        feedback: FeedbackCreate object containing name, email, and message
        
    Returns:
        FeedbackResponse with success message and feedback ID
        
    Raises:
        422: Validation error for invalid input data
        500: Internal server error if database operation fails
    """
    try:
        # Create new feedback record
        db_feedback = Feedback(**feedback.dict())
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        return schemas.FeedbackResponse(
            message="Thank you for your feedback! We appreciate your input.",
            feedback_id=db_feedback.id
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while submitting your feedback. Please try again later."
        )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "API is running"}


@app.get("/health/external-apis")
async def external_apis_health_check():
    """Health check for external APIs."""
    if not settings.enable_external_data:
        return {
            "status": "disabled",
            "message": "External data integration is disabled",
            "apis": {}
        }
    
    try:
        # Use a simple in-memory cache for external data health check
        class SimpleCache:
            def __init__(self):
                self.cache = {}
            
            async def get(self, key):
                return self.cache.get(key)
            
            async def set(self, key, value, ttl=None):
                self.cache[key] = value
        
        cache_service = SimpleCache()
        external_service = get_external_data_service(cache_service)
        health_status = await external_service.health_check()
        
        # Count healthy APIs
        total_apis = len(health_status.get('apis', {}))
        healthy_apis = sum(1 for api_status in health_status.get('apis', {}).values() 
                          if api_status.get('status') == 'healthy')
        
        overall_status = "healthy" if healthy_apis > 0 else "unhealthy"
        if healthy_apis < total_apis:
            overall_status = "partial"
        
        return {
            "status": overall_status,
            "message": f"{healthy_apis}/{total_apis} external APIs are healthy",
            "detail": health_status
        }
        
    except Exception as e:
        api_logger.error(f"External API health check failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "apis": {}
        }


# Cities endpoints
@app.get("/cities", response_model=List[schemas.City])
async def get_cities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all cities with optional pagination."""
    cities = db.query(City).offset(skip).limit(limit).all()
    return cities


@app.get("/city/search", response_model=List[schemas.City])
async def search_cities(
    name: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Search for cities by name (case-insensitive partial match).
    
    Args:
        name: City name to search for (partial match supported)
        limit: Maximum number of results to return (default: 10)
        
    Returns:
        List of cities matching the search criteria with their coordinates
    """
    if not name or len(name.strip()) < 1:
        raise HTTPException(
            status_code=400, 
            detail="City name parameter is required and must be at least 1 character"
        )
    
    # Perform case-insensitive partial match search
    cities = db.query(City).filter(
        City.name.ilike(f"%{name.strip()}%")
    ).limit(limit).all()
    
    return cities


@app.get("/city/search/enhanced")
async def search_cities_enhanced(
    name: str,
    limit: int = 10,
    include_realtime: bool = True,
    db: Session = Depends(get_db)
):
    """
    Enhanced city search with real-time data from external APIs.
    
    Args:
        name: City name to search for (partial match supported)
        limit: Maximum number of results to return (default: 10)
        include_realtime: Whether to include real-time data (weather, news, etc.)
        
    Returns:
        List of cities with enhanced real-time information
    """
    if not name or len(name.strip()) < 1:
        raise HTTPException(
            status_code=400, 
            detail="City name parameter is required and must be at least 1 character"
        )
    
    # Get base city data from database
    cities = db.query(City).filter(
        City.name.ilike(f"%{name.strip()}%")
    ).limit(limit).all()
    
    if not cities:
        return []
    
    enhanced_cities = []
    
    for city in cities:
        # Convert to dict for easier manipulation
        city_data = {
            "id": city.id,
            "name": city.name,
            "country": city.country,
            "state_province": city.state_province,
            "latitude": city.latitude,
            "longitude": city.longitude,
            "population": city.population,
            "area_km2": city.area_km2,
            "description": city.description,
            "realtime_data": None
        }
        
        # Add real-time data if requested and external data is enabled
        if include_realtime and settings.enable_external_data:
            try:
                # Use a simple in-memory cache for external data since we have a different cache system
                class SimpleCache:
                    def __init__(self):
                        self.cache = {}
                    
                    async def get(self, key):
                        return self.cache.get(key)
                    
                    async def set(self, key, value, ttl=None):
                        self.cache[key] = value
                
                cache_service = SimpleCache()
                external_service = get_external_data_service(cache_service)
                
                # Fetch enhanced data
                realtime_data = await external_service.get_enhanced_city_data(
                    city.name, 
                    city.country, 
                    float(city.latitude), 
                    float(city.longitude)
                )
                
                city_data["realtime_data"] = realtime_data
                api_logger.info(f"Enhanced data fetched for {city.name}, {city.country}")
                
            except Exception as e:
                api_logger.error(f"Failed to fetch enhanced data for {city.name}: {str(e)}")
                city_data["realtime_data"] = {
                    "error": "Failed to fetch real-time data",
                    "timestamp": None
                }
        
        enhanced_cities.append(city_data)
    
    return enhanced_cities


@app.get("/cities/{city_id}", response_model=schemas.City)
async def get_city(city_id: int, db: Session = Depends(get_db)):
    """Get a specific city by ID."""
    city = db.query(City).filter(City.id == city_id).first()
    if city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@app.post("/cities", response_model=schemas.City, status_code=status.HTTP_201_CREATED)
async def create_city(
    city: schemas.CityCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """Create a new city (admin only)."""
    db_city = City(**city.dict())
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city


@app.put("/cities/{city_id}", response_model=schemas.City)
async def update_city(
    city_id: int,
    city_data: schemas.CityCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """Update a city (admin only)."""
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    for field, value in city_data.dict().items():
        setattr(city, field, value)
    
    db.commit()
    db.refresh(city)
    return city


@app.delete("/cities/{city_id}")
async def delete_city(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """Delete a city (admin only)."""
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    # Check if city has associated parks
    parks_count = db.query(Park).filter(Park.city_id == city_id).count()
    if parks_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete city with {parks_count} associated parks. Delete parks first."
        )
    
    db.delete(city)
    db.commit()
    return {"message": f"City '{city.name}' deleted successfully"}


# Parks endpoints
@app.get("/parks", response_model=List[schemas.Park])
async def get_parks(
    city_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all parks with optional city filtering and pagination."""
    query = db.query(Park)
    if city_id:
        query = query.filter(Park.city_id == city_id)
    parks = query.offset(skip).limit(limit).all()
    return parks


@app.get("/parks/nearest", response_model=List[schemas.NearestParkResponse])
async def get_nearest_parks(
    latitude: float = Query(..., description="User's latitude", ge=-90, le=90),
    longitude: float = Query(..., description="User's longitude", ge=-180, le=180),
    radius_km: float = Query(5.0, description="Search radius in kilometers", ge=0.1, le=50),
    limit: int = Query(20, description="Maximum number of parks to return", ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Find nearest parks within specified radius from user coordinates.
    
    Args:
        latitude: User's latitude (-90 to 90)
        longitude: User's longitude (-180 to 180)  
        radius_km: Search radius in kilometers (default: 5km, max: 50km)
        limit: Maximum number of results (default: 20, max: 100)
        
    Returns:
        List of parks within radius, sorted by distance, including:
        - Park name, area, and amenities
        - Distance from user location
        - Park coordinates
    """
    # Get all parks with coordinates
    parks = db.query(Park).filter(
        Park.latitude.isnot(None),
        Park.longitude.isnot(None)
    ).all()
    
    if not parks:
        return []
    
    # Calculate distances and filter within radius
    parks_with_distance = []
    for park in parks:
        distance = calculate_distance(latitude, longitude, park.latitude, park.longitude)
        
        if distance <= radius_km:
            parks_with_distance.append({
                "id": park.id,
                "name": park.name,
                "area_hectares": park.area_hectares,
                "amenities": park.facilities,  # Using facilities as amenities
                "distance_km": round(distance, 2),
                "latitude": park.latitude,
                "longitude": park.longitude
            })
    
    # Sort by distance and limit results
    parks_with_distance.sort(key=lambda x: x["distance_km"])
    return parks_with_distance[:limit]


@app.get("/parks/{park_id}", response_model=schemas.Park)
async def get_park(park_id: int, db: Session = Depends(get_db)):
    """Get a specific park by ID."""
    park = db.query(Park).filter(Park.id == park_id).first()
    if park is None:
        raise HTTPException(status_code=404, detail="Park not found")
    return park


@app.post("/parks", response_model=schemas.Park, status_code=status.HTTP_201_CREATED)
async def create_park(
    park: schemas.ParkCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """Create a new park (admin only)."""
    # Verify city exists
    city = db.query(City).filter(City.id == park.city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    db_park = Park(**park.dict())
    db.add(db_park)
    db.commit()
    db.refresh(db_park)
    return db_park


@app.put("/parks/{park_id}", response_model=schemas.Park)
async def update_park(
    park_id: int,
    park_data: schemas.ParkCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """Update a park (admin only)."""
    park = db.query(Park).filter(Park.id == park_id).first()
    if not park:
        raise HTTPException(status_code=404, detail="Park not found")
    
    # Verify city exists if city_id is being changed
    if park_data.city_id != park.city_id:
        city = db.query(City).filter(City.id == park_data.city_id).first()
        if not city:
            raise HTTPException(status_code=404, detail="City not found")
    
    for field, value in park_data.dict().items():
        setattr(park, field, value)
    
    db.commit()
    db.refresh(park)
    return park


@app.delete("/parks/{park_id}")
async def delete_park(
    park_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """Delete a park (admin only)."""
    park = db.query(Park).filter(Park.id == park_id).first()
    if not park:
        raise HTTPException(status_code=404, detail="Park not found")
    
    park_name = park.name
    db.delete(park)
    db.commit()
    return {"message": f"Park '{park_name}' deleted successfully"}


# Green Coverage endpoints
@app.get("/green-coverage", response_model=List[schemas.GreenCoverage])
async def get_green_coverage(
    city_id: Optional[int] = None,
    year: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get green coverage data with optional filtering."""
    query = db.query(GreenCoverage)
    if city_id:
        query = query.filter(GreenCoverage.city_id == city_id)
    if year:
        query = query.filter(GreenCoverage.year == year)
    coverage = query.offset(skip).limit(limit).all()
    return coverage


@app.get("/green-coverage/{coverage_id}", response_model=schemas.GreenCoverage)
async def get_green_coverage_by_id(coverage_id: int, db: Session = Depends(get_db)):
    """Get specific green coverage record by ID."""
    coverage = db.query(GreenCoverage).filter(GreenCoverage.id == coverage_id).first()
    if coverage is None:
        raise HTTPException(status_code=404, detail="Green coverage record not found")
    return coverage


@app.post("/green-coverage", response_model=schemas.GreenCoverage, status_code=status.HTTP_201_CREATED)
async def create_green_coverage(
    coverage: schemas.GreenCoverageCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """Create a new green coverage record (admin only)."""
    # Verify city exists
    city = db.query(City).filter(City.id == coverage.city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    # Check for duplicate city-year combination
    existing = db.query(GreenCoverage).filter(
        GreenCoverage.city_id == coverage.city_id,
        GreenCoverage.year == coverage.year
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Green coverage data for city {coverage.city_id} and year {coverage.year} already exists"
        )
    
    # Set city_name from city record
    coverage_data = coverage.dict()
    coverage_data["city_name"] = city.name
    
    db_coverage = GreenCoverage(**coverage_data)
    db.add(db_coverage)
    db.commit()
    db.refresh(db_coverage)
    return db_coverage


@app.get("/coverage/compare", response_model=schemas.GreenCoverageComparisonResponse)
async def compare_green_coverage(
    city_name: str = Query(..., description="Name of the city to compare green coverage"),
    db: Session = Depends(get_db)
):
    """
    Compare a city's green coverage with WHO recommendations.
    
    Args:
        city_name: Name of the city to analyze
        
    Returns:
        Comparison data including:
        - City's current green coverage percentage
        - WHO recommendation percentage (30% for urban areas)
        - Comparison result description
        - Year of the coverage data used
    """
    # WHO recommends at least 30% green coverage for urban areas
    WHO_RECOMMENDATION_PERCENTAGE = 30.0
    
    # Find the city (case-insensitive search)
    city = db.query(City).filter(City.name.ilike(city_name.strip())).first()
    if not city:
        raise HTTPException(
            status_code=404, 
            detail=f"City '{city_name}' not found"
        )
    
    # Initialize cache service
    cache_service = CacheService(db)
    
    # Define calculation function
    def calculate_comparison():
        # Get the most recent green coverage data for the city
        latest_coverage = db.query(GreenCoverage).filter(
            GreenCoverage.city_id == city.id
        ).order_by(GreenCoverage.year.desc()).first()
        
        if not latest_coverage:
            raise HTTPException(
                status_code=404,
                detail=f"No green coverage data found for city '{city.name}'"
            )
        
        # Generate comparison result string
        city_coverage = latest_coverage.coverage_percentage
        difference = city_coverage - WHO_RECOMMENDATION_PERCENTAGE
        
        if difference >= 0:
            if difference >= 10:
                comparison_result = f"Excellent! {city.name} exceeds WHO recommendations by {difference:.1f} percentage points, indicating a very healthy urban environment."
            elif difference >= 5:
                comparison_result = f"Great! {city.name} exceeds WHO recommendations by {difference:.1f} percentage points, showing good environmental planning."
            else:
                comparison_result = f"Good! {city.name} meets WHO recommendations with {difference:.1f} percentage points above the threshold."
        else:
            abs_difference = abs(difference)
            if abs_difference >= 15:
                comparison_result = f"Critical: {city.name} is {abs_difference:.1f} percentage points below WHO recommendations. Significant improvement in green infrastructure is needed."
            elif abs_difference >= 10:
                comparison_result = f"Below standard: {city.name} is {abs_difference:.1f} percentage points below WHO recommendations. More green spaces are needed."
            elif abs_difference >= 5:
                comparison_result = f"Moderate gap: {city.name} is {abs_difference:.1f} percentage points below WHO recommendations. Additional green initiatives would be beneficial."
            else:
                comparison_result = f"Nearly meets standard: {city.name} is {abs_difference:.1f} percentage points below WHO recommendations. Small improvements would reach the target."
        
        return schemas.GreenCoverageComparisonResponse(
            city_name=city.name,
            city_green_coverage_percentage=city_coverage,
            who_recommendation_percentage=WHO_RECOMMENDATION_PERCENTAGE,
            comparison_result=comparison_result,
            year=latest_coverage.year
        )
    
    # Use cache service to get or calculate comparison
    return cache_service.get_or_calculate_coverage_comparison(
        city_name=city_name.strip(),
        calculation_func=calculate_comparison
    )


@app.get("/coverage/trend", response_model=List[schemas.GreenCoverageTrend])
async def get_green_coverage_trend(
    city_name: str = Query(..., description="Name of the city to get coverage trend for"),
    start_year: Optional[int] = Query(None, description="Start year for trend data"),
    end_year: Optional[int] = Query(None, description="End year for trend data"),
    db: Session = Depends(get_db)
):
    """
    Get historical green coverage trend data for a city.
    
    Args:
        city_name: Name of the city to analyze
        start_year: Optional start year to filter data (inclusive)
        end_year: Optional end year to filter data (inclusive)
        
    Returns:
        List of historical green coverage data ordered by year (ascending) including:
        - Year
        - Green coverage percentage
        - Total area and green area in km²
        - Data source and measurement method
    """
    # Find the city (case-insensitive search)
    city = db.query(City).filter(City.name.ilike(city_name.strip())).first()
    if not city:
        raise HTTPException(
            status_code=404, 
            detail=f"City '{city_name}' not found"
        )
    
    # Build query for historical coverage data
    query = db.query(GreenCoverage).filter(GreenCoverage.city_id == city.id)
    
    # Apply year filters if provided
    if start_year:
        query = query.filter(GreenCoverage.year >= start_year)
    if end_year:
        query = query.filter(GreenCoverage.year <= end_year)
    
    # Order by year ascending for trend visualization
    coverage_data = query.order_by(GreenCoverage.year.asc()).all()
    
    if not coverage_data:
        raise HTTPException(
            status_code=404,
            detail=f"No green coverage trend data found for city '{city.name}'"
        )
    
    # Convert to response format
    trend_data = []
    for coverage in coverage_data:
        trend_data.append(schemas.GreenCoverageTrend(
            year=coverage.year,
            coverage_percentage=coverage.coverage_percentage,
            total_area_km2=coverage.total_area_km2,
            green_area_km2=coverage.green_area_km2,
            data_source=coverage.data_source,
            measurement_method=coverage.measurement_method,
            mean_ndvi=coverage.mean_ndvi,
            created_at=coverage.created_at
        ))
    
    return trend_data


# Statistics endpoints
@app.get("/cities/{city_id}/stats")
async def get_city_stats(city_id: int, db: Session = Depends(get_db)):
    """Get comprehensive statistics for a city."""
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    # Initialize cache service
    cache_service = CacheService(db)
    
    # Define calculation function
    def calculate_stats():
        # Count parks
        park_count = db.query(Park).filter(Park.city_id == city_id).count()
        
        # Get latest green coverage
        latest_coverage = db.query(GreenCoverage).filter(
            GreenCoverage.city_id == city_id
        ).order_by(GreenCoverage.year.desc()).first()
        
        # Calculate total park area
        total_park_area = db.query(Park).filter(Park.city_id == city_id).with_entities(
            db.func.sum(Park.area_hectares)
        ).scalar() or 0
        
        return {
            "city": city,
            "park_count": park_count,
            "total_park_area_hectares": total_park_area,
            "latest_green_coverage": latest_coverage,
            "green_coverage_history": db.query(GreenCoverage).filter(
                GreenCoverage.city_id == city_id
            ).order_by(GreenCoverage.year.desc()).all()
        }
    
    # Use cache service to get or calculate stats
    return cache_service.get_or_calculate_city_stats(
        city_id=city_id,
        city_name=city.name,
        calculation_func=calculate_stats
    )


# Cache management endpoints
@app.get("/cache/stats")
async def get_cache_stats(db: Session = Depends(get_db)):
    """Get statistics about the cache."""
    cache_service = CacheService(db)
    return cache_service.get_cache_stats()


@app.post("/cache/cleanup")
async def cleanup_expired_cache(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """Clean up all expired cache entries (admin only)."""
    cache_service = CacheService(db)
    deleted_count = cache_service.cleanup_all_expired()
    return {"message": f"Cleaned up {deleted_count} expired cache entries"}


@app.delete("/cache/city/{city_name}")
async def invalidate_city_cache(
    city_name: str,
    calculation_type: Optional[str] = Query(None, description="Specific calculation type to invalidate"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """Invalidate cache entries for a specific city (admin only)."""
    cache_service = CacheService(db)
    cache_service.invalidate_city_cache(city_name, calculation_type)
    return {"message": f"Invalidated cache for city '{city_name}'"}


# Background task management endpoints
@app.get("/background-tasks/status")
async def get_background_task_status():
    """Get the current status of background tasks."""
    return background_task_service.get_task_status()


@app.post("/background-tasks/trigger-update")
async def trigger_manual_green_coverage_update(
    city_name: Optional[str] = Query(None, description="Optional city name to update specifically"),
    current_user: schemas.User = Depends(get_admin_user)
):
    """
    Manually trigger green coverage update for all cities or a specific city (admin only).
    
    Args:
        city_name: Optional city name to update. If not provided, updates all cities.
        current_user: Current authenticated admin user
        
    Returns:
        Update results including processed count, errors, and duration
    """
    result = await background_task_service.trigger_manual_update(city_name)
    return result


@app.post("/background-tasks/start")
async def start_background_tasks(current_user: schemas.User = Depends(get_admin_user)):
    """Start the background task scheduler (admin only)."""
    if background_task_service.is_running:
        return {"message": "Background tasks are already running"}
    
    await background_task_service.start_scheduler()
    return {"message": "Background tasks started successfully"}


@app.post("/background-tasks/stop")
async def stop_background_tasks(current_user: schemas.User = Depends(get_admin_user)):
    """Stop the background task scheduler (admin only)."""
    if not background_task_service.is_running:
        return {"message": "Background tasks are not currently running"}
    
    await background_task_service.stop_scheduler()
    return {"message": "Background tasks stopped successfully"}


if __name__ == "__main__":
    import uvicorn
    
    api_logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        app, 
        host=settings.api_host, 
        port=settings.api_port,
        log_level=settings.log_level.lower()
    )